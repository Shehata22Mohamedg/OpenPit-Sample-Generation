from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import openpyxl
import os

app = Flask(__name__)

# Ensure the uploads and output directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('output', exist_ok=True)

def append_qaqc_block(current_serial, hole_name, depth_value, depth_start, depth_to, qaqc_list, std_list, output_rows):
    sample_types = ["Assay", "LS", "RS", "PULP", "GBLANK"]
    for qaqc, std in zip(qaqc_list, std_list):
        if std is not None and depth_start == qaqc:
            output_rows.append([current_serial, hole_name, depth_value, depth_start, depth_to, sample_types[0]])
            for suffix, sample_type in zip("ABCE", sample_types[1:]):
                output_rows.append([f"{current_serial}{suffix}", hole_name, depth_value, depth_start, depth_to, sample_type])
            output_rows.append([f"{current_serial}D", hole_name, depth_value, depth_start, depth_to, f"STD{str(std).zfill(3)}"])
            break
    else:
        output_rows.append([current_serial, hole_name, depth_value, depth_start, depth_to, sample_types[0]])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # File upload
        file = request.files['excel_file']
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            # Get user-defined parameters
            depth_increment = float(request.form.get('depth_increment', 2.5))
            merge_if = float(request.form.get('merge_if', 0.6))

            # Read Excel file
            df = pd.read_excel(file_path)
            
            output_rows = []

            # Process the data
            for index, row in df.iterrows():
                depth_start = 0
                hole_name = row["Hole Name"]
                depth_value = row["Final Depth"]
                current_serial = row["Start Serial"]
                qaqc_values = [row[f"QAQC_{i}"] for i in range(1, 6)]
                std_values = [int(row[f"STD_No_{i}"]) if pd.notna(row[f"STD_No_{i}"]) else None for i in range(1, 6)]

                # Ensure depth_value is numeric
                if isinstance(depth_value, (int, float)):
                    while min(depth_start + depth_increment, depth_value) < depth_value:
                        depth_to = min(depth_start + depth_increment, depth_value)
                        append_qaqc_block(current_serial, hole_name, depth_value, depth_start, depth_to, qaqc_values, std_values, output_rows)
                        current_serial += 1
                        depth_start = depth_to

                    if depth_start < depth_value:
                        remaining_depth = depth_value - depth_start
                        if remaining_depth < merge_if:
                            output_rows[-1][4] = depth_value
                        else:
                            append_qaqc_block(current_serial, hole_name, depth_value, depth_start, depth_value, qaqc_values, std_values, output_rows)
                else:
                    print(f"Non-numeric depth value at row {index + 2}: {depth_value}")

            # Convert to DataFrame
            output_df = pd.DataFrame(output_rows, columns=["SERIAL", "HOLE", "DEPTH", "Depth_From", "Depth_To", "Sample_type"])

            # Separate the STD/GBLANK samples
            df_with_std_or_gblank = output_df[output_df['Sample_type'].str.contains('STD|GBLANK', na=False)]
            df_with_std_or_gblank = df_with_std_or_gblank[["SERIAL", "HOLE", "Depth_From", "Sample_type"]]
            df_other = output_df[~output_df['Sample_type'].str.contains('STD|GBLANK', na=False)]

            # Save CSV files
            output_df.to_csv('output/Generated Samples.csv', index=False)
            df_with_std_or_gblank.to_csv('output/STD Samples.csv', index=False)
            df_other.to_csv('output/Interval Samples.csv', index=False)
            print(df_other.head())
            return render_template("index.html", success=True)

    return render_template("index.html", success=False)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('output', filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 400))
    app.run(debug=True, host = "0.0.0.0", port = port)
