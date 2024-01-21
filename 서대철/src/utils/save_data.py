import os

def save_filtered_data(adults_icu, intubation_data, extubation_data, output_dir, outputs):
    try:
        if outputs == 'all':
            if not adults_icu.empty:
                adults_icu.to_csv(os.path.join(output_dir, 'adults_icu.csv'), index=False)
            if not intubation_data.empty:
                intubation_data.to_csv(os.path.join(output_dir, 'intubation_data.csv'), index=False)
            if not extubation_data.empty:
                extubation_data.to_csv(os.path.join(output_dir, 'extubation_data.csv'), index=False)
        elif outputs == 'patients' and not adults_icu.empty:
            adults_icu.to_csv(os.path.join(output_dir, 'adults_icu.csv'), index=False)
        elif outputs == 'ventilations':
            if not intubation_data.empty:
                intubation_data.to_csv(os.path.join(output_dir, 'intubation_data.csv'), index=False)
            if not extubation_data.empty:
                extubation_data.to_csv(os.path.join(output_dir, 'extubation_data.csv'), index=False)

        print("Data extraction and processing complete. Files saved.")
    except Exception as e:
        print(f"An error occurred while saving the data: {e}")
