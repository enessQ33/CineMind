from flask import Flask, render_template_string, jsonify, request
import requests
import os

app = Flask(__name__)

# API KEY'İNİ BURAYA YAZ (TMDB'den aldığın)
API_KEY = "buraya_api_keyini_yaz"

# Ana sayfa HTML'i
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CineMind - Akıllı Film Asistanın</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #141414;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            padding: 20px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .logo-area {
            display: flex;
            flex-direction: column;
        }
        
        h1 {
            color: #e50914;
            font-size: 28px;
            letter-spacing: -0.5px;
        }
        
        .slogan {
            color: #999;
            font-size: 14px;
            margin-top: 2px;
        }
        
        .search-box {
            padding: 10px 15px;
            border-radius: 25px;
            border: none;
            width: 250px;
            font-size: 14px;
            background: #333;
            color: white;
        }
        
        .search-box::placeholder {
            color: #999;
        }
        
        .film-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .film-card {
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .film-card:hover {
            transform: scale(1.05);
        }
        
        .film-card img {
            width: 100%;
            border-radius: 8px;
            aspect-ratio: 2/3;
            object-fit: cover;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        
        .film-title {
            font-size: 14px;
            margin-top: 8px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .film-year {
            color: #999;
            font-size: 12px;
        }
        
        .detay-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            z-index: 1000;
            padding: 20px;
            overflow-y: auto;
        }
        
        .detay-icerik {
            max-width: 500px;
            margin: 40px auto;
            background: #1f1f1f;
            border-radius: 16px;
            padding: 25px;
            position: relative;
            animation: slideUp 0.3s ease;
        }
        
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .kapat {
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 30px;
            cursor: pointer;
            color: #999;
            transition: color 0.2s;
        }
        
        .kapat:hover {
            color: white;
        }
        
        .detay-poster {
            width: 100%;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.8);
        }
        
        .detay-baslik {
            font-size: 24px;
            margin-bottom: 10px;
            padding-right: 30px;
        }
        
        .detay-puan {
            color: #ffd700;
            margin: 10px 0;
            font-size: 18px;
        }
        
        .detay-ozet {
            line-height: 1.6;
            color: #ddd;
            margin: 20px 0;
            font-size: 15px;
        }
        
        .fragman-btn {
            background: #e50914;
            color: white;
            border: none;
            padding: 14px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
            width: 100%;
            transition: background 0.2s;
        }
        
        .fragman-btn:hover {
            background: #f40612;
        }
        
        .fragman-btn:active {
            transform: scale(0.98);
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #999;
            font-size: 16px;
        }
        
        .loading:after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
        
        .sonuc-yok {
            text-align: center;
            padding: 50px;
            color: #999;
            grid-column: 1 / -1;
        }
        
        @media (max-width: 600px) {
            .header {
                flex-direction: column;
                align-items: stretch;
            }
            
            .search-box {
                width: 100%;
            }
            
            .film-grid {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-area">
            <h1>🎬 CineMind</h1>
            <span class="slogan">akıllı film asistanın</span>
        </div>
        <input type="text" class="search-box" placeholder="Film ara..." id="searchInput">
    </div>
    
    <div id="filmListesi" class="film-grid">
        <div class="loading">Filmler yükleniyor</div>
    </div>
    
    <!-- Detay Modal -->
    <div id="detayModal" class="detay-modal">
        <div class="detay-icerik" id="detayIcerik">
            <!-- İçerik javascript ile doldurulacak -->
        </div>
    </div>
    
    <script>
        const API_KEY = '{{api_key}}';
        
        // Popüler filmleri çek
        async function filmleriYukle() {
            try {
                const response = await fetch(`/api/populer`);
                const filmler = await response.json();
                
                if (filmler.length === 0) {
                    document.getElementById('filmListesi').innerHTML = '<div class="sonuc-yok">Film bulunamadı 😕</div>';
                    return;
                }
                
                let html = '';
                filmler.forEach(film => {
                    const poster = film.poster_path 
                        ? `https://image.tmdb.org/t/p/w200${film.poster_path}`
                        : 'https://via.placeholder.com/200x300?text=Poster+Yok';
                    
                    html += `
                        <div class="film-card" onclick="filmDetay(${film.id})">
                            <img src="${poster}" alt="${film.title}">
                            <div class="film-title">${film.title}</div>
                            <div class="film-year">${film.release_date ? film.release_date.substring(0,4) : '????'}</div>
                        </div>
                    `;
                });
                
                document.getElementById('filmListesi').innerHTML = html;
            } catch(error) {
                console.error('Hata:', error);
                document.getElementById('filmListesi').innerHTML = '<div class="sonuc-yok">Filmler yüklenirken hata oldu 😕<br><small>Lütfen tekrar dene</small></div>';
            }
        }
        
        // Film detayını göster
        async function filmDetay(filmId) {
            try {
                const response = await fetch(`/api/film/${filmId}`);
                const film = await response.json();
                
                const poster = film.poster_path 
                    ? `https://image.tmdb.org/t/p/w500${film.poster_path}`
                    : 'https://via.placeholder.com/500x750?text=Poster+Yok';
                
                const detayHtml = `
                    <span class="kapat" onclick="modalKapat()">&times;</span>
                    <img class="detay-poster" src="${poster}" alt="${film.title}">
                    <h2 class="detay-baslik">${film.title}</h2>
                    <div class="detay-puan">⭐ ${film.vote_average ? film.vote_average.toFixed(1) : '?'}/10</div>
                    <div style="color:#999; margin:10px 0">
                        ${film.runtime ? film.runtime + ' dk' : ''}
                        ${film.release_date ? ' • ' + film.release_date.substring(0,4) : ''}
                    </div>
                    <div class="detay-ozet">${film.overview || 'Bu film için özet bulunamadı.'}</div>
                    <button class="fragman-btn" onclick="fragmanBul(${filmId})">🎬 Fragmanı İzle</button>
                `;
                
                document.getElementById('detayIcerik').innerHTML = detayHtml;
                document.getElementById('detayModal').style.display = 'block';
            } catch(error) {
                alert('Film detayı yüklenirken hata oldu');
            }
        }
        
        // Fragman bul
        async function fragmanBul(filmId) {
            try {
                const response = await fetch(`/api/fragman/${filmId}`);
                const data = await response.json();
                
                if (data.videoUrl) {
                    window.open(data.videoUrl, '_blank');
                } else {
                    alert('Bu film için fragman bulunamadı :(');
                }
            } catch(error) {
                alert('Fragman aranırken hata oldu');
            }
        }
        
        // Modal kapat
        function modalKapat() {
            document.getElementById('detayModal').style.display = 'none';
        }
        
        // Arama
        let aramaTimeout;
        document.getElementById('searchInput').addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            
            // Önceki timeout'u temizle (çok fazla istek gitmesin)
            clearTimeout(aramaTimeout);
            
            if (query.length === 0) {
                filmleriYukle();
                return;
            }
            
            if (query.length > 2) {
                // Kullanıcı yazmayı bitirsin diye biraz bekle
                aramaTimeout = setTimeout(async () => {
                    document.getElementById('filmListesi').innerHTML = '<div class="loading">Aranıyor...</div>';
                    
                    const response = await fetch(`/api/ara?q=${encodeURIComponent(query)}`);
                    const filmler = await response.json();
                    
                    if (filmler.length === 0) {
                        document.getElementById('filmListesi').innerHTML = '<div class="sonuc-yok">Film bulunamadı 😕</div>';
                        return;
                    }
                    
                    let html = '';
                    filmler.forEach(film => {
                        const poster = film.poster_path 
                            ? `https://image.tmdb.org/t/p/w200${film.poster_path}`
                            : 'https://via.placeholder.com/200x300?text=Poster+Yok';
                        
                        html += `
                            <div class="film-card" onclick="filmDetay(${film.id})">
                                <img src="${poster}" alt="${film.title}">
                                <div class="film-title">${film.title}</div>
                                <div class="film-year">${film.release_date ? film.release_date.substring(0,4) : '????'}</div>
                            </div>
                        `;
                    });
                    
                    document.getElementById('filmListesi').innerHTML = html;
                }, 500); // 500ms bekle
            }
        });
        
        // Sayfa açılınca filmleri yükle
        filmleriYukle();
        
        // Modal dışına tıklayınca kapat
        window.onclick = function(event) {
            if (event.target == document.getElementById('detayModal')) {
                modalKapat();
            }
        }
        
        // Escape tuşu ile modal kapat
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                modalKapat();
            }
        });
    </script>
</body>
</html>
"""

# API Rotaları
@app.route('/')
def home():
    return render_template_string(HTML, api_key=API_KEY)

@app.route('/api/populer')
def populer_filmler():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=tr-TR"
    response = requests.get(url)
    return jsonify(response.json()['results'])

@app.route('/api/film/<int:film_id>')
def film_detay(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}?api_key={API_KEY}&language=tr-TR"
    response = requests.get(url)
    return jsonify(response.json())

@app.route('/api/fragman/<int:film_id>')
def film_fragman(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={API_KEY}&language=tr-TR"
    response = requests.get(url)
    videolar = response.json()['results']
    
    # YouTube fragmanı bul
    for video in videolar:
        if video['site'] == 'YouTube' and video['type'] == 'Trailer':
            return jsonify({'videoUrl': f"https://www.youtube.com/watch?v={video['key']}"})
    
    return jsonify({'videoUrl': None})

@app.route('/api/ara')
def film_ara():
    query = request.args.get('q', '')
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}&language=tr-TR"
    response = requests.get(url)
    return jsonify(response.json()['results'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
