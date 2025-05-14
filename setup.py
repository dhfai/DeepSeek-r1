import os
import subprocess

# === Step 1: Input Identitas dari Terminal ===
print("🧠 Buat identitas model Ollama baru:")
model_name     = input("Nama model baru (tanpa spasi): ").strip().lower().replace(" ", "_")
main_model     = input("Base model (contoh: deepseek-r1:1.5b): ").strip()
agent_type     = input("Tipe agen (contoh: guru, Asisten Pendidikan, dll): ")
agent_name     = input("Nama agen (contoh: Raka, Sinta): ")
user_name      = input("Nama pengguna (kamu): ")
agent_relation = input("Hubungan agen ke pengguna (contoh: Pembimbing RPP): ")
agent_attitude = input("Sikap agen (contoh: Ramah, profesional, dan komunikatif): ")

# === Step 2: Baca Template dan Gantikan Placeholder ===
with open("Modelfile-template", "r") as f:
    template = f.read()

template = template.replace("[main_model_source]", main_model)
template = template.replace("[agent_type]", agent_type)
template = template.replace("[agent_name]", agent_name)
template = template.replace("[user_name]", user_name)
template = template.replace("[agent_relation]", agent_relation)
template = template.replace("[agent_attitude]", agent_attitude)

# === Step 3: Simpan sebagai Modelfile sementara ===
temp_modelfile = "Modelfile.temp"
with open(temp_modelfile, "w") as f:
    f.write(template)

# === Step 4: Jalankan `ollama create` ===
print(f"\n⚙️ Membuat model '{model_name}' dari '{main_model}'...")
result = subprocess.run(["ollama", "create", model_name, "-f", temp_modelfile])

# === Step 5: Bersihkan ===
os.remove(temp_modelfile)

# === Step 6: Tampilkan Hasil ===
if result.returncode == 0:
    print(f"\n✅ Model baru '{model_name}' berhasil dibuat! Jalankan dengan:\n\n    ollama run {model_name}\n")
else:
    print("❌ Gagal membuat model.")
