import re
import os

# =====================================================================================
# Fayl nomlari
INPUT_FILE = "Iqtisodiy bilim asoslari. 8-sinf (2014, E.Sariqov, B.Haydarov).txt"
OUTPUT_FILE = "iqtisodiyot_mavzu_savollari.txt" # Natijalar yoziladigan fayl nomi
# =====================================================================================

def extract_questions_to_txt():
    """
    Darslik TXT faylidan har bir mavzu oxiridagi 'BILIMINGIZNI SINAB KO‘RING!' 
    savollarini ajratib oladi va yangi TXT faylga yozadi.
    """
    print(f"'{INPUT_FILE}' faylini o'qish boshlandi...")
    try:
        # Faylni o'qish (UTF-8 kodirovkasida)
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"❌ Xatolik: '{INPUT_FILE}' fayli topilmadi. Fayl nomini tekshiring.")
        return
    except Exception as e:
        print(f"❌ Faylni o'qishda kutilmagan xato: {e}")
        return

    # Natijalarni saqlash uchun lug'at
    extracted_data = {}
    
    # Barcha mavzu bloklarini (1-MAVZU ... keyingi MAVZU / Bob takrorlashigacha) ajratib olish
    # 're.DOTALL' - yangi qatorlarni ham nuqta bilan topishga imkon beradi
    mavzu_blocks = re.findall(
        r'(\d+-MAVZU\s+.+?)(?=\n\d+-MAVZU|\n[IVX]+ bobni takrorlash|\Z)', 
        text, 
        re.DOTALL | re.IGNORECASE
    )

    for mavzu_block in mavzu_blocks:
        # 1. Mavzu nomini ajratib olish (raqami va nomi)
        mavzu_header_match = re.search(r'(\d+)-MAVZU\s+(.+)', mavzu_block, re.IGNORECASE)
        if not mavzu_header_match:
            continue
            
        mavzu_raqami = mavzu_header_match.group(1)
        # Sarlavhadan keyingi ortiqcha qatorlarni olib tashlaymiz
        mavzu_nomi = mavzu_header_match.group(2).split('\n')[0].strip()
        full_mavzu_name = f"{mavzu_raqami}. {mavzu_nomi}"
        
        # 2. 'BILIMINGIZNI SINAB KO‘RING!' qismini topish
        # Savollar qismi: BILIMINGIZNI SINAB KO‘RING! va keyingi katta bo'limgacha
        questions_start_match = re.search(
            r'BILIMINGIZNI SINAB KO‘RING!(.*?)(?=Buni yodda tuting!|IQTIBOSLAR|Qadriyatlar!|\n\d+-MAVZU|\n[IVX]+ bobni takrorlash|\Z)', 
            mavzu_block, 
            re.DOTALL | re.IGNORECASE
        )
        
        if questions_start_match:
            questions_text = questions_start_match.group(1)
            
            # 3. Savollarni raqamlar bo'yicha ajratib olish
            savollar_list = []
            # Savollar raqam (masalan, 1.) va keyin matndan iborat
            raw_questions = re.findall(r'^\s*(\d+)\.\s*(.+?)$', questions_text, re.MULTILINE)
            
            for raqam, savol_matni in raw_questions:
                # Matndagi keraksiz belgilarni tozalash (masalan, "ццц")
                cleaned_question = savol_matni.replace('ццц', '').strip()
                if cleaned_question:
                    savollar_list.append(cleaned_question)
            
            if savollar_list:
                extracted_data[full_mavzu_name] = savollar_list


    # 4. Natijalarni yangi TXT faylga yozish
    output = []
    if not extracted_data:
        print("❌ Xatolik: Faylda hech qanday mavzu savollari topilmadi. Savollar formatini tekshiring.")
        return

    for mavzu, savollar in extracted_data.items():
        output.append("=" * 70)
        output.append(f"MAVZU: {mavzu}")
        output.append("=" * 70)
        
        for i, savol in enumerate(savollar):
            output.append(f"{i + 1}. {savol}")
        output.append("\n\n")

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        print(f"✅ Barcha {len(extracted_data)} mavzuning savollari muvaffaqiyatli '{OUTPUT_FILE}' fayliga yozildi.")
    except Exception as e:
        print(f"❌ Natijalarni yozishda xato yuz berdi: {e}")

if __name__ == "__main__":
    extract_questions_to_txt()