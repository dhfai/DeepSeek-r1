import os
import logging
from pathlib import Path
from src.agents.rpp_agent import RPPAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize RPP Agent
        agent = RPPAgent()

        while True:
            print("\n=== Sistem Pembuatan RPP ===")
            print("1. Proses Dokumen")
            print("2. Buat RPP")
            print("3. Lihat Statistik Sistem")
            print("4. Keluar")

            choice = input("\nPilih menu (1-4): ")

            if choice == "1":
                # Process documents
                doc_dir = input("\nMasukkan path direktori dokumen: ")
                if os.path.exists(doc_dir):
                    print("\nMemproses dokumen...")
                    results = agent.process_documents(doc_dir)
                    print(f"\nBerhasil memproses {results['processed_files']} file")
                    print(f"Total chunks: {results['total_chunks']}")
                else:
                    print("Direktori tidak ditemukan!")

            elif choice == "2":
                # Generate RPP step by step
                print("\n=== Pembuatan RPP ===")
                print("Masukkan detail RPP yang ingin dibuat:")

                mata_pelajaran = input("Mata Pelajaran: ")
                kelas = input("Kelas: ")
                topik = input("Topik: ")
                durasi = input("Durasi (menit): ")

                base_query = f"""
                Buatkan RPP untuk:
                - Mata Pelajaran: {mata_pelajaran}
                - Kelas: {kelas}
                - Topik: {topik}
                - Durasi: {durasi} menit
                """

                context = {
                    "mata_pelajaran": mata_pelajaran,
                    "kelas": kelas,
                    "topik": topik,
                    "durasi": durasi
                }

                # Define the sections to generate
                sections = [
                    "Identitas",
                    "Kompetensi Dasar dan Indikator",
                    "Tujuan Pembelajaran",
                    "Materi Pembelajaran",
                    "Metode Pembelajaran",
                    "Media dan Sumber Belajar",
                    "Langkah Pembelajaran",
                    "Penilaian"
                ]

                # Dictionary to store the final approved sections
                approved_sections = {}

                print("\nMembuat RPP secara bertahap...")

                # Generate each section with user confirmation
                for section in sections:
                    approved = False

                    while not approved:
                        print(f"\n=== Membuat bagian: {section} ===")
                        result = agent.generate_rpp_section(base_query, section, context)

                        print(f"\n=== {section} yang Dihasilkan ===")
                        print(result["section_content"])

                        # Get feedback for this section
                        feedback = input(f"\nApakah bagian {section} sudah sesuai? (y/n): ")

                        if feedback.lower() == 'y':
                            approved = True
                            approved_sections[section] = result["section_content"]
                            print(f"Bagian {section} disetujui!")
                        else:
                            feedback_detail = input("Berikan masukan untuk perbaikan bagian ini: ")
                            agent.get_feedback(
                                result.get("section_name", "unknown"),
                                {
                                    "feedback": feedback_detail,
                                    "section": section,
                                    "context": context
                                }
                            )
                            print(f"Membuat ulang bagian {section} berdasarkan masukan...")

                # Compile the complete RPP after all sections are approved
                if approved_sections:
                    print("\n=== Menyusun RPP Lengkap ===")
                    complete_rpp = agent.compile_full_rpp(approved_sections)

                    print("\n=== RPP LENGKAP ===")
                    print(complete_rpp)

                    # Ask if user wants to save the RPP
                    save_option = input("\nApakah ingin menyimpan RPP ini? (y/n): ")
                    if save_option.lower() == 'y':
                        file_name = f"RPP_{mata_pelajaran.replace(' ', '_')}_{topik.replace(' ', '_')}.md"
                        with open(file_name, "w", encoding="utf-8") as f:
                            f.write(complete_rpp)
                        print(f"RPP berhasil disimpan sebagai '{file_name}'")

            elif choice == "3":
                # Show system stats
                stats = agent.get_system_stats()
                print("\n=== Statistik Sistem ===")
                print("\nVector Store:")
                print(f"- Total dokumen: {stats['vector_store']['count']}")
                print(f"- Nama koleksi: {stats['vector_store']['name']}")

                print("\nMemory Store:")
                print(f"- Total memori: {stats['memory_store']['total_memories']}")
                print("\nJenis Memori:")
                for mem_type, count in stats['memory_store']['memory_types'].items():
                    print(f"- {mem_type}: {count}")

            elif choice == "4":
                print("\nTerima kasih telah menggunakan sistem!")
                break

            else:
                print("\nPilihan tidak valid!")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
