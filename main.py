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
                # Generate RPP
                print("\n=== Pembuatan RPP ===")
                print("Masukkan detail RPP yang ingin dibuat:")

                mata_pelajaran = input("Mata Pelajaran: ")
                kelas = input("Kelas: ")
                topik = input("Topik: ")
                durasi = input("Durasi (menit): ")

                query = f"""
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

                print("\nMembuat RPP...")
                result = agent.generate_rpp(query, context)

                print("\n=== RPP yang Dihasilkan ===")
                print(result["rpp"])

                # Get feedback
                feedback = input("\nApakah RPP sudah sesuai? (y/n): ")
                if feedback.lower() == 'n':
                    feedback_detail = input("Berikan masukan untuk perbaikan: ")
                    agent.get_feedback(
                        result.get("rpp_id", "unknown"),
                        {
                            "feedback": feedback_detail,
                            "context": context
                        }
                    )

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
