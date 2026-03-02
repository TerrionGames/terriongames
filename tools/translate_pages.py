"""
Translate visible UI strings in lovemarble_*.html files using a built-in translation table.
This is a convenience script that performs conservative string replacements for
common phrases (title, meta description, hero text, section titles, card labels,
etc.) and updates `lang` attribute and image folder paths to `images/<lang>/`.

Run from repository root:
  python tools/translate_pages.py

This script edits files in-place. It is safe to review changes via git.
"""
from pathlib import Path
import re

# Minimal translation table for visible phrases.
TRANSLATIONS = {
    'de': {
        'lang': 'de',
        'title': 'Love Marble - Das ultimative Spiel für Paare',
        'meta_desc': 'Offline-Brettspiel für Paare (2 Spieler). Würfle, erledige Missionen und stärke eure Nähe. Verfügbar für iOS & Android.',
        'og_title': 'Love Marble - Das Paar-Brettspiel',
        'og_desc': 'Entfache eure Romantik mit dem ultimativen Brettspiel für Paare!',
        'twitter_title': 'Love Marble - Entfache die Romantik',
        'twitter_desc': 'Das beste Brettspiel für Paare. Würfle und starte eure gemeinsame Reise!',
        'hero_sub': 'Würfle. Entfache die Romantik.',
        'banner_alt': 'Hauptbanner',
        'play_now': 'Jetzt spielen',
        'preview_title': 'In-Game Vorschau',
        'pc_msg': '< Pfeile klicken zum Scrollen >',
        'mobile_msg': 'Wische nach links, um zu erkunden ->',
        'packs_title': 'Kartenpack-Sammlung',
        'card_1_title': 'SÜSS',
        'card_1_sub': 'Romantischer Funke',
        'card_1_desc': 'Erinnere dich an das erste Date! Taucht ein in süße Gespräche und Berührungen.',
        'ready_title': 'Bereit zu spielen?',
        'available': 'Verfügbar für iOS & Android',
        'appstore_alt': 'Im App Store herunterladen',
        'playstore_alt': 'Bei Google Play herunterladen',
        'back': '< TERRION Startseite',
        'footer_dev': 'Entwickelt von Ian & Zonk.'
    },
    'fr': {
        'lang': 'fr',
        'title': 'Love Marble - Le jeu de couple ultime',
        'meta_desc': "Jeu de plateau hors-ligne pour couples (2 joueurs). Lancez les dés, réalisez des missions et renforcez votre complicité. Disponible sur iOS & Android.",
        'og_title': 'Love Marble - Le jeu de couple',
        'og_desc': 'Ravivez votre romance avec le jeu de plateau ultime pour couples!',
        'twitter_title': 'Love Marble - Ravivez la romance',
        'twitter_desc': "Le meilleur jeu de plateau pour couples. Lancez les dés et commencez votre aventure!",
        'hero_sub': 'Lancez les dés. Ravivez la romance.',
        'banner_alt': 'Bannière principale',
        'play_now': 'Jouez maintenant',
        'preview_title': 'Aperçu en jeu',
        'pc_msg': '< Cliquez sur les flèches pour défiler >',
        'mobile_msg': 'Glissez à gauche pour explorer ->',
        'packs_title': 'Collection de packs de cartes',
        'card_1_title': 'Doux',
        'card_1_sub': 'Étincelle romantique',
        'card_1_desc': "Rappelez-vous les papillons du premier rendez-vous! Plongez dans des conversations tendres.",
        'ready_title': 'Prêt à jouer?',
        'available': 'Disponible sur iOS & Android',
        'appstore_alt': 'Télécharger sur l\'App Store',
        'playstore_alt': 'Disponible sur Google Play',
        'back': '< TERRION Accueil',
        'footer_dev': 'Développé par Ian & Zonk.'
    },
    'es': {
        'lang': 'es',
        'title': 'Love Marble - El juego de pareja definitivo',
        'meta_desc': 'Juego de mesa offline para parejas (2 jugadores). Lanza los dados, completa misiones y fortalece la intimidad. Disponible en iOS y Android.',
        'og_title': 'Love Marble - El juego para parejas',
        'og_desc': 'Enciende tu romance con el juego de mesa definitivo para parejas!',
        'twitter_title': 'Love Marble - Enciende el romance',
        'twitter_desc': 'El mejor juego de mesa para parejas. Lanza los dados y comienza tu viaje ahora!',
        'hero_sub': 'Lanza los dados. Enciende el romance.',
        'banner_alt': 'Banner principal',
        'play_now': 'Jugar ahora',
        'preview_title': 'Vista previa en el juego',
        'pc_msg': '< Clica flechas para desplazarte >',
        'mobile_msg': 'Desliza a la izquierda para explorar ->',
        'packs_title': 'Colección de packs de cartas',
        'card_1_title': 'DULCE',
        'card_1_sub': 'Chispa romántica',
        'card_1_desc': '¿Recuerdas la emoción del primer encuentro? Sumérgete en conversaciones dulces y toques románticos.',
        'ready_title': '¿Listo para jugar?',
        'available': 'Disponible en iOS y Android',
        'appstore_alt': 'Descargar en App Store',
        'playstore_alt': 'Obtener en Google Play',
        'back': '< TERRION Inicio',
        'footer_dev': 'Desarrollado por Ian & Zonk.'
    },
    'it': {
        'lang': 'it',
        'title': 'Love Marble - Il gioco di coppia definitivo',
        'meta_desc': 'Gioco da tavolo offline per coppie (2 giocatori). Lancia il dado, completa missioni e costruisci intimità. Disponibile su iOS e Android.',
        'og_title': 'Love Marble - Il gioco per coppie',
        'og_desc': 'Accendi la tua storia d\'amore con il gioco da tavolo definitivo per coppie!',
        'twitter_title': 'Love Marble - Accendi la passione',
        'twitter_desc': 'Il miglior gioco da tavolo per coppie. Lancia il dado e inizia il tuo viaggio ora!',
        'hero_sub': 'Lancia il dado. Accendi la passione.',
        'banner_alt': 'Banner principale',
        'play_now': 'Gioca ora',
        'preview_title': 'Anteprima di gioco',
        'pc_msg': '< Clicca le frecce per scorrere >',
        'mobile_msg': 'Scorri a sinistra per esplorare ->',
        'packs_title': 'Collezione di pacchetti carte',
        'card_1_title': 'DOLCE',
        'card_1_sub': 'Scintilla romantica',
        'card_1_desc': 'Ti ricordi le farfalle del primo appuntamento? Immergiti in dolci conversazioni e carezze romantiche.',
        'ready_title': 'Pronto a giocare?',
        'available': 'Disponibile su iOS e Android',
        'appstore_alt': 'Scarica dall\'App Store',
        'playstore_alt': 'Disponibile su Google Play',
        'back': '< TERRION Home',
        'footer_dev': 'Sviluppato da Ian & Zonk.'
    },
    'ja': {
        'lang': 'ja',
        'title': 'ラブマーブル - カップルのための究極のゲーム',
        'meta_desc': 'オフラインカップルボードゲーム（2人用）。サイコロを振ってミッションをクリアし、親密さを築きましょう。iOSとAndroidで利用可能。',
        'og_title': 'ラブマーブル - カップル向けボードゲーム',
        'og_desc': 'カップルのための究極のボードゲームでロマンスを呼び起こそう！',
        'twitter_title': 'ラブマーブル - ロマンスを呼び起こそう',
        'twitter_desc': 'カップル向け最高のボードゲーム。サイコロを振って今すぐ旅を始めよう！',
        'hero_sub': 'サイコロを振って、ロマンスを呼び起こそう。',
        'banner_alt': 'メインバナー',
        'play_now': '今すぐプレイ',
        'preview_title': 'ゲーム内プレビュー',
        'pc_msg': '< 矢印をクリックしてスクロール >',
        'mobile_msg': '左にスワイプして確認 ->',
        'packs_title': 'カードパックコレクション',
        'card_1_title': 'スイート',
        'card_1_sub': 'ロマンチックなきらめき',
        'card_1_desc': '初デートのときめきを覚えていますか？甘い会話とロマンチックなタッチを楽しんでください。',
        'ready_title': 'プレイの準備はできていますか？',
        'available': 'iOS と Android で利用可能',
        'appstore_alt': 'App Store でダウンロード',
        'playstore_alt': 'Google Play で入手',
        'back': '< TERRION ホーム',
        'footer_dev': '開発: Ian & Zonk.'
    },
    'ko': {
        'lang': 'ko',
        'title': '러브 마블 - 커플을 위한 보드게임',
        'meta_desc': '오프라인 커플 보드게임(2인용). 주사위를 굴리고 미션을 수행하며 둘만의 친밀함을 쌓아보세요. iOS와 Android에서 이용 가능.',
        'og_title': '러브 마블 - 커플 보드게임',
        'og_desc': '커플을 위한 궁극의 보드게임으로 로맨스를 불러오세요!',
        'twitter_title': '러브 마블 - 로맨스를 불러오세요',
        'twitter_desc': '커플을 위한 최고의 보드게임. 주사위를 굴리고 지금 여정을 시작하세요!',
        'hero_sub': '주사위를 굴려 로맨스를 불러오세요.',
        'banner_alt': '메인 배너',
        'play_now': '지금 플레이',
        'preview_title': '게임 화면 미리보기',
        'pc_msg': '< 화살표 클릭하여 스크롤 >',
        'mobile_msg': '왼쪽으로 스와이프하여 확인 ->',
        'packs_title': '카드 팩 모음',
        'card_1_title': '달콤',
        'card_1_sub': '로맨틱 스파크',
        'card_1_desc': '첫 데이트의 설렘을 기억하세요? 달콤한 대화와 터치로 사랑을 키워보세요.',
        'ready_title': '지금 플레이할 준비 되셨나요?',
        'available': 'iOS 및 Android에서 이용 가능',
        'appstore_alt': 'App Store에서 다운로드',
        'playstore_alt': 'Google Play에서 다운로드',
        'back': '< TERRION 홈',
        'footer_dev': '개발: Ian & Zonk.'
    },
    'zh-TW': {
        'lang': 'zh-TW',
        'title': 'Love Marble - 情侶專屬桌遊',
        'meta_desc': '離線情侶桌遊（2 人）。擲骰子、完成任務，增進親密關係。支援 iOS 與 Android。',
        'og_title': 'Love Marble - 情侶桌遊',
        'og_desc': '用這款情侶專屬桌遊點燃你們的浪漫！',
        'twitter_title': 'Love Marble - 點燃浪漫',
        'twitter_desc': '最佳情侶桌遊。擲骰子，立即開始你們的旅程！',
        'hero_sub': '擲骰子。點燃浪漫。',
        'banner_alt': '主橫幅',
        'play_now': '立即遊玩',
        'preview_title': '遊戲畫面預覽',
        'pc_msg': '< 點擊箭頭以滾動 >',
        'mobile_msg': '向左滑動以瀏覽 ->',
        'packs_title': '卡牌包合集',
        'card_1_title': '甜蜜',
        'card_1_sub': '浪漫火花',
        'card_1_desc': '還記得第一次約會的悸動嗎？沉浸在甜蜜對話與浪漫互動中吧。',
        'ready_title': '準備好遊玩了嗎？',
        'available': '支援 iOS 與 Android',
        'appstore_alt': '在 App Store 下載',
        'playstore_alt': '在 Google Play 取得',
        'back': '< TERRION 首頁',
        'footer_dev': '開發: Ian & Zonk.'
    },
    'th': {
        'lang': 'th',
        'title': 'Love Marble - เกมบอร์ดคู่รักที่ดีที่สุด',
        'meta_desc': 'เกมบอร์ดออฟไลน์สำหรับคู่รัก (2 ผู้เล่น) ทอยลูกเต๋า ทำภารกิจ และสร้างความใกล้ชิด มีให้บน iOS และ Android',
        'og_title': 'Love Marble - เกมคู่รัก',
        'og_desc': 'จุดประกายความโรแมนติกของคุณด้วยเกมบอร์ดคู่รัก!',
        'twitter_title': 'Love Marble - จุดประกายความรัก',
        'twitter_desc': 'เกมบอร์ดที่ดีที่สุดสำหรับคู่รัก ทอยลูกเต๋าและเริ่มการผจญภัยของคุณ!',
        'hero_sub': 'ทอยลูกเต๋า จุดประกายความรัก',
        'banner_alt': 'แบนเนอร์หลัก',
        'play_now': 'เล่นเลย',
        'preview_title': 'ตัวอย่างในเกม',
        'pc_msg': '< คลิกลูกศรเพื่อเลื่อน >',
        'mobile_msg': 'ปัดซ้ายเพื่อสำรวจ ->',
        'packs_title': 'คอลเลคชันการ์ดแพ็ค',
        'card_1_title': 'หวาน',
        'card_1_sub': 'ประกายโรแมนติก',
        'card_1_desc': 'จำความตื่นเต้นของเดทแรกได้ไหม? ดื่มด่ำกับบทสนทนาหวาน ๆ และสัมผัสอบอุ่น',
        'ready_title': 'พร้อมเล่นหรือยัง?',
        'available': 'ใช้ได้บน iOS และ Android',
        'appstore_alt': 'ดาวน์โหลดจาก App Store',
        'playstore_alt': 'ดาวน์โหลดจาก Google Play',
        'back': '< TERRION โฮม',
        'footer_dev': 'พัฒนาโดย Ian & Zonk.'
    },
    'vi': {
        'lang': 'vi',
        'title': 'Love Marble - Trò chơi cặp đôi tối thượng',
        'meta_desc': 'Trò chơi bàn offline cho cặp đôi (2 người). Lắc xúc xắc, hoàn thành nhiệm vụ và xây dựng sự thân mật. Có trên iOS & Android.',
        'og_title': 'Love Marble - Trò chơi cho cặp đôi',
        'og_desc': 'Khơi dậy lãng mạn với trò chơi bàn tối thượng cho cặp đôi!',
        'twitter_title': 'Love Marble - Khơi dậy lãng mạn',
        'twitter_desc': 'Trò chơi bàn tốt nhất cho cặp đôi. Lắc xúc xắc và bắt đầu hành trình ngay!',
        'hero_sub': 'Lắc xúc xắc. Khơi dậy lãng mạn.',
        'banner_alt': 'Biểu ngữ chính',
        'play_now': 'Chơi ngay',
        'preview_title': 'Xem trước trong game',
        'pc_msg': '< Nhấn mũi tên để cuộn >',
        'mobile_msg': 'Vuốt sang trái để khám phá ->',
        'packs_title': 'Bộ sưu tập gói thẻ',
        'card_1_title': 'NGỌT',
        'card_1_sub': 'Tia lửa lãng mạn',
        'card_1_desc': 'Bạn còn nhớ cảm giác rung động lần đầu gặp gỡ không? Đắm chìm trong những cuộc trò chuyện ngọt ngào và những cử chỉ lãng mạn.',
        'ready_title': 'Sẵn sàng chơi?',
        'available': 'Có trên iOS & Android',
        'appstore_alt': 'Tải trên App Store',
        'playstore_alt': 'Nhận trên Google Play',
        'back': '< TERRION Trang chủ',
        'footer_dev': 'Phát triển: Ian & Zonk.'
    },
    'id': {
        'lang': 'id',
        'title': 'Love Marble - Game pasangan terbaik',
        'meta_desc': 'Game papan offline untuk pasangan (2 pemain). Gulir dadu, selesaikan misi, dan bangun keintiman. Tersedia di iOS & Android.',
        'og_title': 'Love Marble - Game untuk pasangan',
        'og_desc': 'Nyalakan romansa Anda dengan game papan terbaik untuk pasangan!',
        'twitter_title': 'Love Marble - Nyalakan romansa',
        'twitter_desc': 'Game papan terbaik untuk pasangan. Gulir dadu dan mulai perjalanan Anda sekarang!',
        'hero_sub': 'Gulir dadu. Nyalakan romansa.',
        'banner_alt': 'Banner utama',
        'play_now': 'Main sekarang',
        'preview_title': 'Pratinjau dalam game',
        'pc_msg': '< Klik panah untuk menggulir >',
        'mobile_msg': 'Geser ke kiri untuk menjelajah ->',
        'packs_title': 'Koleksi paket kartu',
        'card_1_title': 'MANIS',
        'card_1_sub': 'Percikan Romantis',
        'card_1_desc': 'Ingat detak jantung pada kencan pertama? Selami percakapan manis dan sentuhan romantis.',
        'ready_title': 'Siap bermain?',
        'available': 'Tersedia di iOS & Android',
        'appstore_alt': 'Unduh di App Store',
        'playstore_alt': 'Dapatkan di Google Play',
        'back': '< TERRION Beranda',
        'footer_dev': 'Dikembangkan oleh Ian & Zonk.'
    },
    'hi': {
        'lang': 'hi',
        'title': 'लव मार्बल - जोड़ों के लिए अल्टीमेट गेम',
        'meta_desc': 'ऑफलाइन कपल बोर्ड गेम (2 खिलाड़ियों के लिए)। पासा फेंकें, मिशन पूरा करें और निकटता बनाएं। iOS और Android पर उपलब्ध।',
        'og_title': 'लव मार्बल - कपल बोर्ड गेम',
        'og_desc': 'जोड़ों के लिए अल्टीमेट बोर्ड गेम से अपने रोमांस को जगाइए!',
        'twitter_title': 'लव मार्बल - रोमांस जगाइए',
        'twitter_desc': 'जोड़ों के लिए सर्वश्रेष्ठ बोर्ड गेम। पासा फेंकें और अपनी यात्रा शुरू करें!',
        'hero_sub': 'पासा फेंकें। रोमांस जगाइए।',
        'banner_alt': 'मुख्य बैनर',
        'play_now': 'अब खेलें',
        'preview_title': 'इन-गेम पूर्वावलोकन',
        'pc_msg': '< स्क्रॉल करने के लिए तीर पर क्लिक करें >',
        'mobile_msg': 'खोजने के लिए बाएं स्वाइप करें ->',
        'packs_title': 'कार्ड पैक संग्रह',
        'card_1_title': 'मीठा',
        'card_1_sub': 'रोमांटिक चिंगारी',
        'card_1_desc': 'क्या आपको पहले डेट की धड़कन याद है? मीठी बातचीत और रोमांटिक टच में डूब जाएं।',
        'ready_title': 'खेलने के लिए तैयार?',
        'available': 'iOS और Android पर उपलब्ध',
        'appstore_alt': 'App Store पर डाउनलोड करें',
        'playstore_alt': 'Google Play पर प्राप्त करें',
        'back': '< TERRION होम',
        'footer_dev': 'डेवेलप्ड बाय Ian & Zonk.'
    },
    'pt-BR': {
        'lang': 'pt-BR',
        'title': 'Love Marble - O jogo de casal definitivo',
        'meta_desc': 'Jogo de tabuleiro offline para casais (2 jogadores). Role o dado, complete missões e construa intimidade. Disponível no iOS e Android.',
        'og_title': 'Love Marble - Jogo para casais',
        'og_desc': 'Acenda seu romance com o jogo de tabuleiro definitivo para casais!',
        'twitter_title': 'Love Marble - Acenda o romance',
        'twitter_desc': 'O melhor jogo de tabuleiro para casais. Role o dado e comece sua jornada agora!',
        'hero_sub': 'Role o dado. Acenda o romance.',
        'banner_alt': 'Banner principal',
        'play_now': 'Jogar agora',
        'preview_title': 'Prévia no jogo',
        'pc_msg': '< Clique nas setas para rolar >',
        'mobile_msg': 'Deslize para a esquerda para explorar ->',
        'packs_title': 'Coleção de pacotes de cartas',
        'card_1_title': 'DOCE',
        'card_1_sub': 'Faísca romântica',
        'card_1_desc': 'Lembra a emoção do primeiro encontro? Mergulhe em conversas doces e toques românticos.',
        'ready_title': 'Pronto para jogar?',
        'available': 'Disponível no iOS e Android',
        'appstore_alt': 'Baixar na App Store',
        'playstore_alt': 'Disponível no Google Play',
        'back': '< TERRION Início',
        'footer_dev': 'Desenvolvido por Ian & Zonk.'
    },
    'ru': {
        'lang': 'ru',
        'title': 'Love Marble - Игра для пар',
        'meta_desc': 'Оффлайн настольная игра для пар (2 игрока). Бросайте кости, выполняйте задания и укрепляйте близость. Доступно на iOS и Android.',
        'og_title': 'Love Marble - Настольная игра для пар',
        'og_desc': 'Зажгите романтику с лучшей настольной игрой для пар!',
        'twitter_title': 'Love Marble - Зажгите романтику',
        'twitter_desc': 'Лучшая настольная игра для пар. Бросайте кости и начните путешествие сейчас!',
        'hero_sub': 'Бросайте кости. Зажгите романтику.',
        'banner_alt': 'Главный баннер',
        'play_now': 'Играть сейчас',
        'preview_title': 'Превью в игре',
        'pc_msg': '< Нажмите стрелки для прокрутки >',
        'mobile_msg': 'Проведите влево, чтобы исследовать ->',
        'packs_title': 'Коллекция наборов карт',
        'card_1_title': 'СЛАДКОЕ',
        'card_1_sub': 'Романтическая искра',
        'card_1_desc': 'Помните трепет первого свидания? Погрузитесь в сладкие разговоры и романтические прикосновения.',
        'ready_title': 'Готовы играть?',
        'available': 'Доступно на iOS и Android',
        'appstore_alt': 'Скачать в App Store',
        'playstore_alt': 'Получить в Google Play',
        'back': '< TERRION Главная',
        'footer_dev': 'Разработано Ian & Zonk.'
    }
    ,
    'tr': {
        'lang': 'tr',
        'title': 'Love Marble - Çiftler için nihai oyun',
        'meta_desc': 'Çevrimdışı çiftler için masa oyunu (2 oyuncu). Zar atın, görevleri tamamlayın ve samimiyeti artırın. iOS ve Android üzerinde mevcut.',
        'og_title': 'Love Marble - Çiftler için masa oyunu',
        'og_desc': 'Çiftler için en iyi masa oyunu ile romantizmi yakın!',
        'twitter_title': 'Love Marble - Romantizmi yakın',
        'twitter_desc': 'Çiftler için en iyi masa oyunu. Zar atın ve yolculuğunuza hemen başlayın!',
        'hero_sub': 'Zarı atın. Romantizmi yakın.',
        'banner_alt': 'Ana afiş',
        'play_now': 'Şimdi oyna',
        'preview_title': 'Oyun İçi Önizleme',
        'pc_msg': '< Kaydırmak için okları tıklayın >',
        'mobile_msg': 'Keşfetmek için sola kaydır ->',
        'packs_title': 'Kart Paketi Koleksiyonu',
        'card_1_title': 'TATLI',
        'card_1_sub': 'Romantik kıvılcım',
        'card_1_desc': 'İlk buluşmanın heyecanını hatırlıyor musunuz? Tatlı sohbetlere ve romantik dokunuşlara dalın.',
        'ready_title': 'Oynamaya hazır mısınız?',
        'available': 'iOS ve Android üzerinde mevcut',
        'appstore_alt': 'App Store\'dan indir',
        'playstore_alt': 'Google Play\'den al',
        'back': '< TERRION Ana Sayfa',
        'footer_dev': 'Geliştiren: Ian & Zonk.'
    }
}

# Map file suffix to language key in TRANSLATIONS
FILE_LANG_MAP = {
    'lovemarble_de.html': 'de',
    'lovemarble_fr.html': 'fr',
    'lovemarble_es-ES.html': 'es',
    'lovemarble_es-MX.html': 'es',
    'lovemarble_it.html': 'it',
    'lovemarble_ja.html': 'ja',
    'lovemarble_zh-TW.html': 'zh-TW',
    'lovemarble_th.html': 'th',
    'lovemarble_vi.html': 'vi',
    'lovemarble_id.html': 'id',
    'lovemarble_hi.html': 'hi',
    'lovemarble_pt-BR.html': 'pt-BR',
    'lovemarble_ru.html': 'ru',
    'lovemarble_tr.html': 'tr',
    'lovemarble_ko.html': 'ko'
}

ROOT = Path('.').resolve()

TEMPLATE_KEYS = [
    ('<html lang="en">', lambda t: f'<html lang="{t["lang"]}">'),
    ('<title>Love Marble - The Ultimate Couple Game</title>', lambda t: f'<title>{t["title"]}</title>'),
    ('<meta name="description" content="An offline couple board game for 2 players on 1 device. Roll the dice, complete sweet missions, and build intimacy. Available on App Store and Google Play.">',
     lambda t: f'<meta name="description" content="{t["meta_desc"]}">'),
    ('<meta property="og:title" content="Love Marble - The Ultimate Couple Board Game">', lambda t: f'<meta property="og:title" content="{t["og_title"]}">'),
    ('<meta property="og:description" content="Spark your romance with the ultimate board game for couples! 16 languages supported. 100% private & no server required.">',
     lambda t: f'<meta property="og:description" content="{t["og_desc"]}">'),
    ('<meta name="twitter:title" content="Love Marble - Spark the Romance">', lambda t: f'<meta name="twitter:title" content="{t["twitter_title"]}">'),
    ('<meta name="twitter:description" content="The best board game for couples. Roll the dice and start your journey now!">', lambda t: f'<meta name="twitter:description" content="{t["twitter_desc"]}">'),
    ('<p style="font-size: 1.2rem; color: var(--text-secondary);">Roll the dice. Spark the romance.</p>', lambda t: f'<p style="font-size: 1.2rem; color: var(--text-secondary);">{t["hero_sub"]}</p>'),
    ('<span class="alt-text">Main Banner Loading...</span>', lambda t: f'<span class="alt-text">{t["banner_alt"]} 로딩 중...</span>' if t.get('lang','').startswith('ko') else f'<span class="alt-text">{t["banner_alt"]} Loading...</span>' ),
    ('<a href="#download" id="hero-down-btn" class="btn">Play Now</a>', lambda t: f'<a href="#download" id="hero-down-btn" class="btn">{t["play_now"]}</a>'),
    ('<h2 class="section-title"><span>In-Game Preview</span></h2>', lambda t: f'<h2 class="section-title"><span>{t["preview_title"]}</span></h2>'),
    ('<span class="pc-msg">&lt; Click Arrows to Scroll &gt;</span>', lambda t: f'<span class="pc-msg">{t["pc_msg"]}</span>'),
    ('<span class="mobile-msg">Swipe left to explore -></span>', lambda t: f'<span class="mobile-msg">{t["mobile_msg"]}</span>'),
    ('<h2 class="section-title"><span>Card Packs Collection</span></h2>', lambda t: f'<h2 class="section-title"><span>{t["packs_title"]}</span></h2>'),
    ('Ready to Play?', lambda t: t['ready_title']),
    ('Available on iOS & Android', lambda t: t['available']),
    ('alt="Download on the App Store"', lambda t: f'alt="{t["appstore_alt"]}"'),
    ('alt="Get it on Google Play"', lambda t: f'alt="{t["playstore_alt"]}"'),
    ('&copy; 2026 TERRION Games. <br>\n        Developed by Ian & Zonk.', lambda t: f'&copy; 2026 TERRION Games. <br>\n        {t["footer_dev"]}')
]

# Card pack replacements (a subset)
CARD_REPLACEMENTS = [
    (r'>🍭 SWEET</h3>', lambda t: f'>🍭 {t.get("card_1_title", "SWEET")}</h3>'),
    (r'>Romantic Spark</span>', lambda t: f'>{t.get("card_1_sub","Romantic Spark")}</span>'),
    (r'>Remember that first-date flutter\? Dive into sweet talk and romantic touches!</p>',
     lambda t: f'>{t.get("card_1_desc","Remember that first-date flutter? Dive into sweet talk and romantic touches!")}</p>')
]


def translate_file(path: Path, lang_key: str):
    print('Translating', path.name, '->', lang_key)
    if lang_key not in TRANSLATIONS:
        print('No translations for', lang_key)
        return
    t = TRANSLATIONS[lang_key]
    text = path.read_text(encoding='utf-8')

    # Replace image/icon paths
    text = text.replace('images/icon.png', f'images/{t["lang"]}/icon.png')
    text = text.replace('IMG_CONFIG = {\n            folder: "./images/', 'IMG_CONFIG = {\n            folder: "./images/')
    # Update IMG_CONFIG.folder pattern more directly
    text = re.sub(r"folder:\s*\"\.\/images\/.{0,10}\",", f'folder: "./images/{t["lang"]}/",', text)

    # Apply template key replacements
    for orig, fn in TEMPLATE_KEYS:
        if isinstance(orig, str) and orig in text:
            new = fn(t)
            text = text.replace(orig, new)

    # Simple card replacements
    for pattern, fn in CARD_REPLACEMENTS:
        text = re.sub(pattern, fn(t), text)

    # Update html lang attribute if present
    text = re.sub(r'<html lang="[^"]+">', f'<html lang="{t["lang"]}">', text)

    path.write_text(text, encoding='utf-8')


def main():
    files = [p for p in Path('.').glob('lovemarble_*.html')]
    for f in files:
        key = FILE_LANG_MAP.get(f.name)
        if not key:
            print('Skipping', f.name)
            continue
        translate_file(f, key)

    print('Done translating files.')

if __name__ == '__main__':
    main()
