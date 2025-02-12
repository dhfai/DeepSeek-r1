# Ollama DeepSeek and LLAMA

### Install

- Install dependencies menggunakan perintah `pip install -r requirements.txt`


### Configuration

_Make sure Ollama service is running before configuring._

- `python3 setup.py` - terlebih dahulu jalankan perintah ini untuk mengatur konfigurasi agent yang akan dibuat. Perintah ini akan menulis ke `config.json` yang diperlukan oleh skrip utama `converse.py` dan `app.py`. Jika ingin menjalankan perintah ini lagi, hapus `config.json` yang sudah ada.
- (opsional) scrape PDFs. Lihat bagian tentang ini di bawah

### Run

_Make sure Ollama service is running before running._

- `./run.sh` atau `python3 app.py`  - akan menjalankan aplikasi web yang dapat diakses melalui browser di `http://localhost:8401`



## Detail Lainnya

### Ollama

Ollama adalah pelari LLM praktis yang memiliki banyak repositori yang dikonfigurasi dengan model paling populer yang siap digunakan. Ini berjalan pada CPU jadi jika Anda menggunakan Macbook Pro yang agak lama (seperti saya), Anda dapat menjalankan LLM secara lokal.

Ini sangat keren karena input/output percakapan yang disimulasikan tidak keluar dari komputer Anda. Mampu menjalankannya sendiri secara lokal merupakan kepemilikan positif atas data Anda, melindungi privasi Anda, dan memungkinkan Anda bereksperimen secara bebas dengan lebih percaya diri.

Namun, berjalan dengan CPU akan menjadi _jauh_ lebih lambat, jadi ingatlah hal itu.

### RAG and ChromaDB

Proyek ini sementara masih dalam tahap pengembangan dan eksperimen, untuk itu disini kita masih menggunakan RAG (Retrieve and Generate) sebagai model yang digunakan oleh LLM.

Proyek ini menggunakan apa yang disebut database vektor yang disebut ChromaDB, yang memungkinkan traversal cepat terhadap kumpulan data besar bahkan pada perangkat keras terbatas (seperti Macbook Pro Anda yang terpercaya namun agak tua).

Hal ini memperkuat kegunaan LLM dengan memberikan memori dan konteks yang berdekatan di luar jendela konteks sebenarnya dari LLM, yang saat ini cukup kecil untuk LLM yang dijalankan secara lokal.

Efeknya adalah memberikan percakapan yang disimulasikan lebih nyata, terasa seperti manusia, serta berpotensi berguna sebagai cara untuk mencari (untuk 'berbicara') dengan koleksi PDF Anda, menjaga serangkaian percakapan terkait berlangsung dalam jangka waktu yang lama. waktu selama beberapa sesi.


## Catatan Penting

Saya mendorong Anda untuk berhati-hati dalam menggunakan ini. Anda dapat melakukan banyak hal dengannya yang bukan ide bagus. Ini adalah proyek mainan yang dimaksudkan untuk bereksperimen dengan teknologi. Jangan menggunakannya untuk membahayakan kesehatan mental Anda atau orang lain.

## Referensi

Code dan ide dasar diambil dari komunitas Ollama di github, tapi ada beberapa sumber yang paling banyak saya gunakan yaitu dari username `digithree` di github. Terima kasih banyak untuk kontribusi dan kerja kerasnya.

Profile github: <a href="https://github.com/digithree">digithree</a>