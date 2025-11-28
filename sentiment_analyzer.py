import json
import re
from collections import Counter
import string

# 2. Kalit so'zlar asosida oddiy sentiment lug'atini tuzish
# Bu so'zlar tahlil qilinayotgan matn ichidan qidiriladi.
positive_words = {
    "yaxshi", "a'lo", "zo'r", "samarali", "muvaffaqiyatli", "himoya", 
    "rivojlanish", "qo'llab-quvvatlash", "do'stona", "foydali", "ishonchli",
    "mustahkam", "xursand", "baxtli", "tinchlik", "hamkorlik", "omad", 
    "faol", "sog'lom", "yordam", "baxtina"
}

# Salbiy (Negativ) kalit so'zlar
negative_words = {
    "xatolik", "xavf", "ogohlantirish", "xavotir", "muammo", "noto'g'ri", 
    "yomon", "cheklash", "qiyinchilik", "qo'rqitish", "shubhali", "jinoyatchi",
    "aldash", "noqonuniy", "buzilish", "o'g'irlik", "kuchsiz", "fail",
    "qoldirgan", "chetlashtirish", "qarzdorligi", "urinadi"
}

def extract_all_words(json_data):
    """
    JSON ma'lumotlaridan barcha matnlarni ajratib oladi va so'zlarga ajratadi.
    """
    all_text = ""
    if 'messages' not in json_data:
        return []

    for message in json_data['messages']:
        raw_text = message.get('text')
        text_parts = []
        
        if isinstance(raw_text, str):
            text_parts.append(raw_text)
        elif isinstance(raw_text, list):
            for item in raw_text:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])

        text_content = " ".join(text_parts).strip()
        all_text += " " + text_content

    # Matnni kichik harfga o'tkazish
    all_text_lower = all_text.lower()
    
    # Punktuatsiya (tinish belgilari)ni o'chirish
    # O'zbek tiliga xos bo'lmagan ba'zi belgilar ham o'chiriladi.
    translator = str.maketrans('', '', string.punctuation + '«»—’`ʻ')
    cleaned_text = all_text_lower.translate(translator)
    
    # So'zlarga ajratish va bo'sh so'zlarni olib tashlash
    words = [word.strip() for word in cleaned_text.split() if word.strip()]
    return words

def analyze_words(words):
    """So'zlarni sentiment bo'yicha tahlil qiladi va hisoblaydi."""
    
    # Barcha noyob so'zlarni sanash
    all_unique_words_counter = Counter(words)
    
    # Sentiment tahlili uchun so'zlarni sanash
    positive_count = 0
    negative_count = 0
    
    positive_words_found = Counter()
    negative_words_found = Counter()
    
    for word, count in all_unique_words_counter.items():
        if word in positive_words:
            positive_words_found[word] = count
            positive_count += count
        elif word in negative_words:
            negative_words_found[word] = count
            negative_count += count

    total_words = len(words)
    total_polar_words = positive_count + negative_count

    positive_percent = (positive_count / total_polar_words) * 100 if total_polar_words > 0 else 0
    negative_percent = (negative_count / total_polar_words) * 100 if total_polar_words > 0 else 0
    
    return {
        'total_words': total_words,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'total_polar_words': total_polar_words,
        'positive_percent': positive_percent,
        'negative_percent': negative_percent,
        'positive_words_found': positive_words_found,
        'negative_words_found': negative_words_found,
        'all_unique_words_counter': all_unique_words_counter
    }

# 3. Tahlilni amalga oshirish va natijani faylga yozish
if __name__ == "__main__":
    file_path = 'result.json'
    # Natijalar saqlanadigan fayl nomi o'zgartirildi
    output_file_path = 'sentiment_analysis_all_words_results.txt' 
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Xatolik: '{file_path}' fayli topilmadi.")
        exit()
    except json.JSONDecodeError:
        print(f"Xatolik: '{file_path}' fayli noto'g'ri JSON formatida.")
        exit()

    # So'zlarni ajratib olish va tahlil qilish
    all_words = extract_all_words(data)
    results = analyze_words(all_words)
    
    # 4. Natijalarni yozish uchun matn (string) shaklida tayyorlash
    output_content = ""
    output_content += "="*100 + "\n"
    output_content += "✨ Barcha So'zlar Bo'yicha Sentiment Tahlil Natijalari (result.json asosida) ✨" + "\n"
    output_content += "="*100 + "\n"
    
    # Statistikani chiqarish
    output_content += "\n📊 UMUMIY TAHLIL XULOSASI:\n"
    output_content += f"   Matndagi jami so'zlar soni (takroriy so'zlar bilan): {results['total_words']}\n"
    output_content += f"   Lug'atda topilgan (Pozitiv/Negativ) so'zlar soni (takroriy so'zlar bilan): {results['total_polar_words']}\n"
    output_content += f"   Pozitiv so'zlar soni: {results['positive_count']}\n"
    output_content += f"   Negativ so'zlar soni: {results['negative_count']}\n"
    output_content += f"   Pozitiv so'zlar foizi (polar so'zlarga nisbatan): {results['positive_percent']:.2f}%\n"
    output_content += f"   Negativ so'zlar foizi (polar so'zlarga nisbatan): {results['negative_percent']:.2f}%\n"
    output_content += "\n" + "="*100 + "\n"

    # Pozitiv so'zlar ro'yxati
    output_content += "\n🟢 POZITIV SO'ZLAR RO'YXATI (Takrorlanish soni bilan):\n"
    if results['positive_words_found']:
        sorted_pos = sorted(results['positive_words_found'].items(), key=lambda item: item[1], reverse=True)
        for word, count in sorted_pos:
            output_content += f"  - {word}: {count} marta\n"
    else:
        output_content += "  Pozitiv so'zlar lug'atda topilmadi.\n"

    output_content += "\n" + "-"*100 + "\n"

    # Negativ so'zlar ro'yxati
    output_content += "\n🔴 NEGATIV SO'ZLAR RO'YXATI (Takrorlanish soni bilan):\n"
    if results['negative_words_found']:
        sorted_neg = sorted(results['negative_words_found'].items(), key=lambda item: item[1], reverse=True)
        for word, count in sorted_neg:
            output_content += f"  - {word}: {count} marta\n"
    else:
        output_content += "  Negativ so'zlar lug'atda topilmadi.\n"

    output_content += "\n" + "="*100 + "\n"
    
    # Barcha noyob so'zlar ro'yxati
    output_content += "\n📜 BARCHA NOYOB SO'ZLAR VA ULARNING SENTIMENT HOLATI (Ortib borish tartibida):\n"
    
    all_unique_sorted = sorted(results['all_unique_words_counter'].items(), key=lambda item: item[0])
    
    for word, count in all_unique_sorted:
        sentiment = "Neytral"
        if word in positive_words:
            sentiment = "Pozitiv"
        elif word in negative_words:
            sentiment = "Negativ"
            
        output_content += f"  - {word} ({count} marta): {sentiment}\n"

    output_content += "\n" + "="*100 + "\n"

    # 5. Natijani faylga saqlash
    try:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write(output_content)
        
        # 6. Terminalga xabar berish
        print("="*60)
        print(f"✅ Tahlil natijalari muvaffaqiyatli saqlandi!")
        print(f"Fayl nomi: {output_file_path}")
        print(f"Endi bu faylda barcha so'zlar ro'yxati, foizlar va sonlar mavjud.")
        print("="*60)

    except Exception as e:
        print(f"Xatolik: Natijalarni faylga yozishda muammo yuzaga keldi: {e}")
