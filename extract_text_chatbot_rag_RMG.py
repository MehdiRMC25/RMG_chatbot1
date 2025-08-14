import os
from docx import Document

# ✅ Folder and filenames
folder_path = r"C:\Users\Mehdi\Documents\GitHub\RMG Policies"
filenames = [
    "RMG company and products info.docx",
    "RMG How to engage with us.docx",
    "RMG Objectives and Approach.docx"
]

# ✅ Folder where the final policy.txt should be saved
output_folder = r"C:\Users\Mehdi\Documents\GitHub\RMG_chatbot1"

# ✅ Extract and combine
all_text = ""
for file in filenames:
    full_path = os.path.join(folder_path, file)
    doc = Document(full_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])
    all_text += f"\n\n--- {file} ---\n\n{text}"

# ✅ Write to .txt
output_file = os.path.join(output_folder, "policy.txt")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(all_text)

print(f"✅ Extracted text saved to: {output_file}")
