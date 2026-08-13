import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import savgol_filter


def save_noise_removed_csvs(
    root_folder,
    transistor_type,
    temperature,
    remove_noise=True,
    *,
    min_floor_points=4,
    max_floor_points=15, #20
    floor_max_span_decades=0.60,
    floor_max_trend_decades=0.40,#0.25
    min_turnon_rise_decades=0.75,
    noise_sigma_multiplier=2.0, #2.0
    minimum_noise_margin_decades=0.20,#0.2
    smoothing_window=5,
    smoothing_polyorder=2
):
    """
    Searches through transistor subfolders inside root_folder and saves
    noise-removed copies of the original CSV files.

    It also saves a diagnostic plot for every Id-Vg curve showing:
        - points retained in the noise-removed CSV
        - points eliminated from the noise-removed CSV
        - the estimated noise-floor center
        - the elimination threshold

    Output structure
    ----------------
    root_folder/
        transistor_folder/
            original_file.csv

        _noise_removed/
            transistor_folder/
                original_file_noise_removed.csv

            plots/
                transistor_folder/
                    original_file_noise_removed.png

    Behavior
    --------
    Id-Vg curves:
        - Detect whether a low-current noise-floor plateau exists.
        - If a floor is detected, eliminate points at or below the
          calculated noise threshold.
        - If no floor is detected, retain every original row.

    Id-Vd and other CSV files:
        - Retain every original row.
        - No diagnostic plot is created.

    The saved CSV retains exactly the same columns and column order as
    the original file.
    """

    transistor_type_lower = str(transistor_type).lower()

    # ==============================================================
    # Create output folders
    # ==============================================================

    noise_removed_root = os.path.join(
        root_folder,
        "_noise_removed"
    )

    plots_root = os.path.join(
        noise_removed_root,
        "plots"
    )

    os.makedirs(
        noise_removed_root,
        exist_ok=True
    )

    os.makedirs(
        plots_root,
        exist_ok=True
    )

    # ==============================================================
    # Helper functions
    # ==============================================================

    def get_turn_on_coordinate(vgate):
        """
        Return a coordinate that increases from off-state toward on-state.

        nMOS:
            Higher Vg means more strongly on.

        pMOS:
            More negative Vg means more strongly on, so -Vg is used.
        """

        vgate = np.asarray(
            vgate,
            dtype=float
        )

        if transistor_type_lower.startswith("p"):
            return -vgate

        return vgate

    def make_valid_savgol_window(
        number_of_points,
        requested_window,
        polyorder
    ):
        """
        Return a valid odd Savitzky-Golay window length.

        Returns None when there are too few points to smooth safely.
        """

        if number_of_points <= polyorder + 1:
            return None

        window = min(
            requested_window,
            number_of_points
        )

        if window % 2 == 0:
            window -= 1

        if window <= polyorder:
            return None

        return window

    def robust_sigma(values):
        """
        Estimate standard deviation using the median absolute deviation.
        """

        values = np.asarray(
            values,
            dtype=float
        )

        values = values[
            np.isfinite(values)
        ]

        if len(values) == 0:
            return np.nan

        median_value = np.median(
            values
        )

        median_absolute_deviation = np.median(
            np.abs(
                values - median_value
            )
        )

        sigma = (
            1.4826
            * median_absolute_deviation
        )

        # Fall back to ordinary standard deviation if the MAD is zero.
        if not np.isfinite(sigma) or sigma == 0:
            sigma = np.std(
                values
            )

        if not np.isfinite(sigma):
            sigma = 0.0

        return float(sigma)

    def detect_noise_floor(
        vgate,
        drain_current
    ):
        """
        Determine whether an Id-Vg curve contains a low-current
        noise-floor plateau.

        The curve is ordered from transistor off-state toward on-state.

        A noise floor is accepted only when the beginning of the curve:
            1. Contains at least min_floor_points.
            2. Has limited current variation.
            3. Has little systematic upward trend.
            4. Is followed by a clear turn-on current increase.

        Returns
        -------
        dict
            floor_detected
            noise_floor_A
            noise_threshold_A
            smoothed_log_current
            floor_point_mask
            detection_reason
        """

        vgate = np.asarray(
            vgate,
            dtype=float
        )

        drain_current = np.asarray(
            drain_current,
            dtype=float
        )

        number_of_points = len(
            drain_current
        )

        no_floor_result = {
            "floor_detected": False,
            "noise_floor_A": np.nan,
            "noise_threshold_A": np.nan,
            "smoothed_log_current": np.full(
                number_of_points,
                np.nan
            ),
            "floor_point_mask": np.zeros(
                number_of_points,
                dtype=bool
            ),
            "detection_reason": (
                "no_noise_floor_detected"
            )
        }

        valid_mask = (
            np.isfinite(vgate)
            & np.isfinite(drain_current)
            & (drain_current > 0)
        )

        valid_indices = np.flatnonzero(
            valid_mask
        )

        if len(valid_indices) < min_floor_points + 2:
            no_floor_result["detection_reason"] = (
                "not_enough_valid_points"
            )

            return no_floor_result

        turn_on_coordinate = get_turn_on_coordinate(
            vgate
        )

        # Sort points from the transistor off-state toward the on-state.
        sorted_indices = valid_indices[
            np.argsort(
                turn_on_coordinate[
                    valid_indices
                ]
            )
        ]

        sorted_coordinate = turn_on_coordinate[
            sorted_indices
        ]

        sorted_current = drain_current[
            sorted_indices
        ]

        sorted_log_current = np.log10(
            sorted_current
        )

        window_length = make_valid_savgol_window(
            number_of_points=len(
                sorted_log_current
            ),
            requested_window=smoothing_window,
            polyorder=smoothing_polyorder
        )

        if window_length is not None:
            sorted_log_smooth = savgol_filter(
                sorted_log_current,
                window_length=window_length,
                polyorder=smoothing_polyorder,
                mode="interp"
            )

        else:
            sorted_log_smooth = (
                sorted_log_current.copy()
            )

        # Return smoothed values to the original CSV row ordering.
        smoothed_log_original_order = np.full(
            number_of_points,
            np.nan
        )

        smoothed_log_original_order[
            sorted_indices
        ] = sorted_log_smooth

        number_to_test = min(
            max_floor_points,
            len(sorted_indices) - 2
        )

        best_candidate = None

        # ----------------------------------------------------------
        # Test progressively larger prefixes of the off-to-on curve.
        # ----------------------------------------------------------
        for number_floor_points in range(
            min_floor_points,
            number_to_test + 1
        ):
            candidate_log = sorted_log_smooth[
                :number_floor_points
            ]

            candidate_coordinate = sorted_coordinate[
                :number_floor_points
            ]

            # Robust current span inside the possible floor.
            q10, q90 = np.percentile(
                candidate_log,
                [10, 90]
            )

            floor_span_decades = (
                q90 - q10
            )

            # Determine whether the candidate region already has a
            # systematic upward trend.
            coordinate_range = np.ptp(
                candidate_coordinate
            )

            if coordinate_range > 0:
                slope, _ = np.polyfit(
                    candidate_coordinate,
                    candidate_log,
                    1
                )

                floor_trend_decades = abs(
                    slope
                    * coordinate_range
                )

            else:
                floor_trend_decades = 0.0

            floor_center_log10 = np.median(
                candidate_log
            )

            later_log_current = sorted_log_smooth[
                number_floor_points:
            ]

            if len(later_log_current) == 0:
                continue

            later_high_current_log10 = np.percentile(
                later_log_current,
                90
            )

            later_rise_decades = (
                later_high_current_log10
                - floor_center_log10
            )

            global_low_log10 = np.percentile(
                sorted_log_smooth,
                10
            )

            candidate_near_low_current_end = (
                floor_center_log10
                <= global_low_log10
                + floor_max_span_decades
            )

            candidate_has_small_span = (
                floor_span_decades
                <= floor_max_span_decades
            )

            candidate_has_small_trend = (
                floor_trend_decades
                <= floor_max_trend_decades
            )

            candidate_followed_by_turn_on = (
                later_rise_decades
                >= min_turnon_rise_decades
            )

            candidate_is_noise_floor = (
                candidate_near_low_current_end
                and candidate_has_small_span
                and candidate_has_small_trend
                and candidate_followed_by_turn_on
            )

            if candidate_is_noise_floor:
                # Keep the largest candidate that still behaves as a floor.
                best_candidate = {
                    "number_floor_points": (
                        number_floor_points
                    )
                }

        # No sufficiently flat initial plateau was found.
        if best_candidate is None:
            no_floor_result[
                "smoothed_log_current"
            ] = smoothed_log_original_order

            no_floor_result["detection_reason"] = (
                "current_rises_without_noise_plateau"
            )

            return no_floor_result

        number_floor_points = best_candidate[
            "number_floor_points"
        ]

        floor_indices = sorted_indices[
            :number_floor_points
        ]

        floor_point_mask = np.zeros(
            number_of_points,
            dtype=bool
        )

        floor_point_mask[
            floor_indices
        ] = True

        # Use the unsmoothed current values to estimate the floor level.
        floor_log_values = sorted_log_current[
            :number_floor_points
        ]

        floor_center_log10 = np.median(
            floor_log_values
        )

        floor_sigma_log10 = robust_sigma(
            floor_log_values
        )

        if not np.isfinite(
            floor_sigma_log10
        ):
            floor_sigma_log10 = 0.0

        threshold_margin_decades = max(
            noise_sigma_multiplier
            * floor_sigma_log10,
            minimum_noise_margin_decades
        )

        noise_threshold_log10 = (
            floor_center_log10
            + threshold_margin_decades
        )

        noise_floor_A = (
            10.0 ** floor_center_log10
        )

        noise_threshold_A = (
            10.0 ** noise_threshold_log10
        )

        return {
            "floor_detected": True,
            "noise_floor_A": noise_floor_A,
            "noise_threshold_A": (
                noise_threshold_A
            ),
            "smoothed_log_current": (
                smoothed_log_original_order
            ),
            "floor_point_mask": (
                floor_point_mask
            ),
            "detection_reason": (
                "noise_floor_detected"
            )
        }

    def save_idvg_classification_plot(
        vgate,
        measured_current,
        considered_mask,
        floor_result,
        plot_filepath,
        plot_title
    ):
        """
        Save an Id-Vg diagnostic plot showing retained and eliminated points.
        """

        vgate = np.asarray(
            vgate,
            dtype=float
        )

        measured_current = np.asarray(
            measured_current,
            dtype=float
        )

        considered_mask = np.asarray(
            considered_mask,
            dtype=bool
        )

        valid_plot_mask = (
            np.isfinite(vgate)
            & np.isfinite(measured_current)
            & (measured_current > 0)
        )

        considered_plot_mask = (
            valid_plot_mask
            & considered_mask
        )

        eliminated_plot_mask = (
            valid_plot_mask
            & ~considered_mask
        )

        figure, axis = plt.subplots(
            figsize=(9, 6)
        )

        # Draw a thin line through the complete measured curve to make
        # the sweep shape and point ordering easy to see.
        axis.plot(
            vgate[valid_plot_mask],
            measured_current[valid_plot_mask],
            linewidth=1.0,
            alpha=0.6,
            label="Complete measured curve"
        )

        if np.any(considered_plot_mask):
            axis.scatter(
                vgate[considered_plot_mask],
                measured_current[considered_plot_mask],
                marker="o",
                s=38,
                label=(
                    "Considered points "
                    f"(n={np.count_nonzero(considered_plot_mask)})"
                ),
                zorder=3
            )

        if np.any(eliminated_plot_mask):
            axis.scatter(
                vgate[eliminated_plot_mask],
                measured_current[eliminated_plot_mask],
                marker="x",
                s=55,
                linewidths=1.6,
                label=(
                    "Eliminated points "
                    f"(n={np.count_nonzero(eliminated_plot_mask)})"
                ),
                zorder=4
            )

        floor_detected = floor_result[
            "floor_detected"
        ]

        if floor_detected:
            floor_point_mask = floor_result[
                "floor_point_mask"
            ]

            floor_plot_mask = (
                valid_plot_mask
                & floor_point_mask
            )

            if np.any(floor_plot_mask):
                axis.scatter(
                    vgate[floor_plot_mask],
                    measured_current[floor_plot_mask],
                    marker="s",
                    facecolors="none",
                    s=90,
                    linewidths=1.5,
                    label="Detected plateau candidate",
                    zorder=5
                )

            noise_floor_A = floor_result[
                "noise_floor_A"
            ]

            noise_threshold_A = floor_result[
                "noise_threshold_A"
            ]

            axis.axhline(
                noise_floor_A,
                linestyle="--",
                linewidth=1.5,
                label=(
                    "Noise-floor center "
                    f"= {noise_floor_A:.3e} A"
                )
            )

            axis.axhline(
                noise_threshold_A,
                linestyle=":",
                linewidth=1.8,
                label=(
                    "Elimination threshold "
                    f"= {noise_threshold_A:.3e} A"
                )
            )

            plot_note = (
                "Noise floor detected\n"
                "Points at or below the threshold were removed"
            )

        else:
            plot_note = (
                "No noise floor detected\n"
                "All original points were retained"
            )

        axis.text(
            0.02,
            0.98,
            plot_note,
            transform=axis.transAxes,
            verticalalignment="top",
            bbox={
                "boxstyle": "round",
                "alpha": 0.85
            }
        )

        axis.set_yscale(
            "log"
        )

        axis.set_xlabel(
            "Gate voltage, Vg (V)"
        )

        axis.set_ylabel(
            "|Drain current|, |Id| (A)"
        )

        axis.set_title(
            plot_title
        )

        axis.grid(
            True,
            which="both",
            alpha=0.3
        )

        axis.legend()
        axis.set_yscale('log')

        figure.tight_layout()


        # plt.show()
        figure.savefig(
            plot_filepath,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close(
            figure
        )

    def should_exclude_idvd_curve(
            transistor_type,
            temperature,
            gate_bias,
            atol=1e-3
    ):
        """
        Return True when an entire Id-Vd curve should be excluded based on
        transistor type, temperature, and fixed gate-voltage bias.
        """

        transistor_type_lower = str(transistor_type).lower()

        if transistor_type_lower.startswith("n"):
            device_key = "nmos"
        elif transistor_type_lower.startswith("p"):
            device_key = "pmos"
        else:
            return False

        # Use magnitude so pMOS biases stored as negative values still match.
        gate_bias_abs = abs(float(gate_bias))

        exclusion_rules = {
            ("nmos", 300.0): [0.37],
            ("pmos", 300.0): [0.37],

            ("nmos", 77.0): [0.37],
            ("pmos", 77.0): [0.37, 0.74, 1.11],
        } # determined by looking at the curves and determining that these had substantial drain currents

        excluded_biases = exclusion_rules.get(
            (device_key, float(temperature)),
            []
        )

        return any(
            np.isclose(
                gate_bias_abs,
                excluded_bias,
                atol=atol
            )
            for excluded_bias in excluded_biases
        )

    # ==============================================================
    # Process all subfolders inside root_folder
    # ==============================================================

    total_files_saved = 0
    total_plots_saved = 0
    total_idvg_filtered = 0
    total_idvg_unchanged = 0
    noise_log = []

    for folder_name in sorted(
        os.listdir(root_folder)
    ):
        # Do not recursively process generated outputs.
        if folder_name == "_noise_removed":
            continue

        subfolder_path = os.path.join(
            root_folder,
            folder_name
        )

        if not os.path.isdir(
            subfolder_path
        ):
            continue

        noise_removed_subfolder = os.path.join(
            noise_removed_root,
            folder_name
        )

        plot_subfolder = os.path.join(
            plots_root,
            folder_name
        )

        os.makedirs(
            noise_removed_subfolder,
            exist_ok=True
        )

        os.makedirs(
            plot_subfolder,
            exist_ok=True
        )

        csv_files = sorted(
            file
            for file in os.listdir(
                subfolder_path
            )
            if file.lower().endswith(".csv")
        )

        for file in csv_files:
            filepath = os.path.join(
                subfolder_path,
                file
            )

            try:
                df = pd.read_csv(
                    filepath
                )

            except Exception as error:
                print(
                    f"Could not read {filepath}: "
                    f"{error}"
                )
                continue

            file_lower = file.lower()

            file_stem, file_extension = (
                os.path.splitext(file)
            )

            output_filename = (
                f"{file_stem}_noise_removed"
                f"{file_extension}"
            )

            output_filepath = os.path.join(
                noise_removed_subfolder,
                output_filename
            )

            plot_filename = (
                f"{file_stem}_noise_removed.png"
            )

            plot_filepath = os.path.join(
                plot_subfolder,
                plot_filename
            )

            noise_cutoff_vgate = np.nan

            # By default, retain every original row.
            df_noise_removed = df.copy()
            considered_mask = np.ones(
                len(df),
                dtype=bool
            )

            floor_result = {
                "floor_detected": False,
                "noise_floor_A": np.nan,
                "noise_threshold_A": np.nan,
                "smoothed_log_current": np.full(
                    len(df),
                    np.nan
                ),
                "floor_point_mask": np.zeros(
                    len(df),
                    dtype=bool
                ),
                "detection_reason": (
                    "not_an_idvg_curve"
                )
            }

            # ------------------------------------------------------
            # Filter and plot Id-Vg files
            # ------------------------------------------------------
            if "idvg" in file_lower:
                required_columns = {
                    "vgate",
                    "idrain"
                }

                missing_columns = (
                    required_columns.difference(
                        df.columns
                    )
                )

                if missing_columns:
                    print(
                        f"{filepath} is missing "
                        f"{sorted(missing_columns)}. "
                        f"Saving unchanged without a plot."
                    )

                    result_message = (
                        "missing required columns; "
                        "all rows retained"
                    )

                    total_idvg_unchanged += 1

                else:
                    vgate = pd.to_numeric(
                        df["vgate"],
                        errors="coerce"
                    ).to_numpy(dtype=float)

                    measured_current = np.abs(
                        pd.to_numeric(
                            df["idrain"],
                            errors="coerce"
                        ).to_numpy(dtype=float)
                    )

                    if remove_noise:
                        floor_result = detect_noise_floor(
                            vgate=vgate,
                            drain_current=measured_current
                        )

                        if floor_result["floor_detected"]:
                            noise_threshold_A = floor_result[
                                "noise_threshold_A"
                            ]

                            smoothed_log_current = floor_result[
                                "smoothed_log_current"
                            ]

                            valid_current_mask = (
                                np.isfinite(vgate)
                                & np.isfinite(measured_current)
                                & (measured_current > 0)
                            )

                            # Points initially classified as noise
                            initial_noise_mask = (
                                    valid_current_mask
                                    & np.isfinite(smoothed_log_current)
                                    & (
                                            smoothed_log_current
                                            <= np.log10(noise_threshold_A)
                                    )
                            )

                            # Start by retaining every point
                            eliminated_mask = np.zeros(
                                len(df),
                                dtype=bool
                            )

                            if np.any(initial_noise_mask):

                                noisy_vgate = vgate[
                                    initial_noise_mask
                                ]

                                if transistor_type_lower.startswith("p"):
                                    # pMOS turns on as Vg becomes more negative.
                                    # The last noisy point toward turn-on is therefore
                                    # the most negative noisy Vg.
                                    noise_cutoff_vgate = np.min(
                                        noisy_vgate
                                    )

                                    # Remove every point on the off-state side through
                                    # the most-negative noisy point.
                                    #
                                    # Example:
                                    # noisy cutoff = -0.5 V
                                    # eliminate Vg >= -0.5 V
                                    eliminated_mask = (
                                            np.isfinite(vgate)
                                            & (vgate >= noise_cutoff_vgate)
                                    )

                                else:
                                    # nMOS turns on as Vg becomes more positive.
                                    # The last noisy point toward turn-on is therefore
                                    # the most positive noisy Vg.
                                    noise_cutoff_vgate = np.max(
                                        noisy_vgate
                                    )

                                    # Remove every point on the off-state side through
                                    # the most-positive noisy point.
                                    #
                                    # Example:
                                    # noisy cutoff = 0.5 V
                                    # eliminate Vg <= 0.5 V
                                    eliminated_mask = (
                                            np.isfinite(vgate)
                                            & (vgate <= noise_cutoff_vgate)
                                    )

                                considered_mask = (
                                    ~eliminated_mask
                                )

                            else:
                                # The floor was detected, but no points fell below the
                                # calculated threshold. Keep the entire curve.
                                noise_cutoff_vgate = np.nan

                                considered_mask = np.ones(
                                    len(df),
                                    dtype=bool
                                )

                            df_noise_removed = df.loc[
                                considered_mask
                            ].copy()

                            removed_count = (
                                len(df)
                                - len(df_noise_removed)
                            )

                            result_message = (
                                "noise floor detected; "
                                f"{removed_count} rows removed"
                            )

                            total_idvg_filtered += 1

                        else:
                            # No floor means the transistor begins turning
                            # on without a detectable plateau. Keep all rows.
                            considered_mask = np.ones(
                                len(df),
                                dtype=bool
                            )

                            df_noise_removed = df.copy()

                            result_message = (
                                "no noise floor detected; "
                                "all rows retained"
                            )

                            total_idvg_unchanged += 1

                    else:
                        considered_mask = np.ones(
                            len(df),
                            dtype=bool
                        )

                        df_noise_removed = df.copy()

                        floor_result[
                            "detection_reason"
                        ] = "noise_removal_disabled"

                        result_message = (
                            "noise removal disabled; "
                            "all rows retained"
                        )

                        total_idvg_unchanged += 1

                    # Try to extract a fixed drain bias for the plot title.
                    if "vdrain" in df.columns:
                        vdrain_values = pd.to_numeric(
                            df["vdrain"],
                            errors="coerce"
                        ).to_numpy(dtype=float)

                        finite_vdrain = vdrain_values[
                            np.isfinite(vdrain_values)
                        ]

                        if len(finite_vdrain) > 0:
                            drain_bias_text = (
                                f", Vd = {finite_vdrain[0]:g} V"
                            )
                        else:
                            drain_bias_text = ""

                    else:
                        drain_bias_text = ""

                    plot_title = (
                        f"{folder_name}\n"
                        f"{transistor_type} Id-Vg"
                        f"{drain_bias_text}\n"
                        f"{file}"
                    )

                    save_idvg_classification_plot(
                        vgate=vgate,
                        measured_current=measured_current,
                        considered_mask=considered_mask,
                        floor_result=floor_result,
                        plot_filepath=plot_filepath,
                        plot_title=plot_title
                    )

                    total_plots_saved += 1

            # ------------------------------------------------------
            # Handle Id-Vd output characteristic curves
            # ------------------------------------------------------
            elif "idvd" in file_lower:

                if "vgate" not in df.columns:
                    print(
                        f"{filepath} is missing 'vgate'. "
                        f"Saving unchanged."
                    )

                    df_noise_removed = df.copy()

                    considered_mask = np.ones(
                        len(df),
                        dtype=bool
                    )

                    result_message = (
                        "Id-Vd curve missing gate-bias column; "
                        "all rows retained"
                    )

                else:
                    vgate_values = pd.to_numeric(
                        df["vgate"],
                        errors="coerce"
                    ).to_numpy(dtype=float)

                    finite_vgate = vgate_values[
                        np.isfinite(vgate_values)
                    ]

                    if len(finite_vgate) == 0:
                        print(
                            f"{filepath} has no finite gate-bias value. "
                            f"Saving unchanged."
                        )

                        df_noise_removed = df.copy()

                        considered_mask = np.ones(
                            len(df),
                            dtype=bool
                        )

                        result_message = (
                            "Id-Vd curve has no finite gate bias; "
                            "all rows retained"
                        )

                    else:
                        fixed_gate_bias = finite_vgate[0]

                        exclude_entire_curve = should_exclude_idvd_curve(
                            transistor_type=transistor_type,
                            temperature=temperature,
                            gate_bias=fixed_gate_bias
                        )

                        if exclude_entire_curve:
                            print(
                                f"Excluded entire Id-Vd curve: {filepath}\n"
                                f"  transistor type: {transistor_type}\n"
                                f"  temperature: {temperature:g} K\n"
                                f"  |Vg|: {abs(fixed_gate_bias):g} V"
                            )

                            # Do not save this CSV at all.
                            #
                            # Add it to the log first, then skip to the next file.
                            noise_log.append({
                                "folder": folder_name,
                                "file": file,
                                "transistor_type": transistor_type,
                                "temperature_K": temperature,
                                "curve_type": "IdVd",
                                "gate_bias_V": fixed_gate_bias,
                                "gate_bias_abs_V": abs(fixed_gate_bias),
                                "curve_excluded": True,
                                "exclusion_reason": (
                                    "excluded_by_temperature_device_and_gate_bias_rule"
                                ),
                                "floor_detected": False,
                                "detection_reason": "entire_idvd_curve_excluded",
                                "rows_original": len(df),
                                "rows_saved": 0,
                                "rows_removed": len(df),
                                "percent_removed": (
                                    100.0 if len(df) > 0 else 0.0
                                ),
                                "noise_floor_A": np.nan,
                                "noise_threshold_A": np.nan,
                                "noise_cutoff_vgate_V": np.nan,
                                "noise_removed_file": ""
                            })

                            continue

                        else:
                            df_noise_removed = df.copy()

                            considered_mask = np.ones(
                                len(df),
                                dtype=bool
                            )

                            result_message = (
                                "Id-Vd curve retained; "
                                "all rows saved"
                            )

            # ------------------------------------------------------
            # Any other CSV type
            # ------------------------------------------------------
            else:
                df_noise_removed = df.copy()

                considered_mask = np.ones(
                    len(df),
                    dtype=bool
                )

                result_message = (
                    "unrecognized curve type; "
                    "all rows retained"
                )

            # ------------------------------------------------------
            # Save copy with original columns and column order
            # ------------------------------------------------------
            df_noise_removed.reset_index(
                drop=True,
                inplace=True
            )

            df_noise_removed.to_csv(
                output_filepath,
                index=False
            )

            # -----------------------------------------
            # Save information about this processed file
            # -----------------------------------------

            noise_log.append({
                "folder": folder_name,
                "file": file,
                "transistor_type": transistor_type,
                "noise_removed_file": output_filepath,

                "curve_type": (
                    "IdVg" if "idvg" in file_lower
                    else "IdVd"
                ),

                "floor_detected": floor_result["floor_detected"],
                "detection_reason": floor_result["detection_reason"],

                "rows_original": len(df),
                "rows_saved": len(df_noise_removed),
                "rows_removed": len(df) - len(df_noise_removed),

                "percent_removed":
                    100 * (len(df) - len(df_noise_removed))
                    / len(df),

                "noise_floor_A": floor_result["noise_floor_A"],
                "noise_threshold_A": floor_result["noise_threshold_A"],

                # Save the settings used so you know what parameters
                # produced this result.
                "min_floor_points": min_floor_points,
                "max_floor_points": max_floor_points,
                "floor_max_span_decades": floor_max_span_decades,
                "floor_max_trend_decades": floor_max_trend_decades,
                "min_turnon_rise_decades": min_turnon_rise_decades,
                "noise_sigma_multiplier": noise_sigma_multiplier,
                "minimum_noise_margin_decades": minimum_noise_margin_decades,
                "smoothing_window": smoothing_window,
                "smoothing_polyorder": smoothing_polyorder,
                "noise_cutoff_vgate_V": noise_cutoff_vgate,
                "first_saved_vgate_V": (
                    df_noise_removed["vgate"].iloc[0]
                    if (
                            len(df_noise_removed) > 0
                            and "vgate" in df_noise_removed.columns
                    )
                    else np.nan
                ),
            })

            total_files_saved += 1

            print(
                f"Saved CSV: {output_filepath}\n"
                f"  {result_message}\n"
                f"  Rows saved: "
                f"{len(df_noise_removed)}/{len(df)}"
            )

            if "idvg" in file_lower and not {
                "vgate",
                "idrain"
            }.difference(df.columns):
                print(
                    f"Saved plot: {plot_filepath}"
                )

    print(
        "\nFinished saving noise-removed CSV files and plots."
    )

    print(
        f"Noise-removed CSV folder:\n"
        f"{noise_removed_root}"
    )

    print(
        f"Plot folder:\n"
        f"{plots_root}"
    )

    print(
        f"Total CSV files saved: "
        f"{total_files_saved}"
    )

    print(
        f"Total Id-Vg plots saved: "
        f"{total_plots_saved}"
    )

    print(
        f"Id-Vg files filtered: "
        f"{total_idvg_filtered}"
    )

    print(
        f"Id-Vg files retained unchanged: "
        f"{total_idvg_unchanged}"
    )
    # -----------------------------------------
    # Save processing log
    # -----------------------------------------

    noise_log_df = pd.DataFrame(noise_log)

    noise_log_path = os.path.join(
        noise_removed_root,
        "noise_removal_log.csv"
    )

    noise_log_df.to_csv(
        noise_log_path,
        index=False
    )

    print(f"\nNoise removal log saved to:\n{noise_log_path}")

transistor_type = "pMOS"

save_noise_removed_csvs(
    root_folder=f"cryomodels_data_CSV/{transistor_type}/csvs/",
    transistor_type=transistor_type,
    temperature=77,
    remove_noise=True
)

