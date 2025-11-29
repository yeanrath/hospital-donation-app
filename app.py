import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- ផ្នែកកំណត់ការកំណត់ (Configuration) ---
TEMPLATE_FILE = "appreciation_template.png"
FONT_FILE = "KhmerOSmuollight.ttf" # ប្រាកដថាឈ្មោះ Font ត្រូវនឹង File ក្នុង Folder

# កំណត់ទីតាំង និងទំហំអក្សរ
NAME_FONT_SIZE = 50
NAME_Y_POS = 780      
NAME_COLOR = (50, 89, 158) 

AMOUNT_FONT_SIZE = 50
AMOUNT_Y_POS = 850     
AMOUNT_COLOR = (192, 57, 43) 

# --- ១. មុខងាររក្សាទុកចូល GOOGLE SHEETS (បន្ថែមថ្មី) ---
def save_to_google_sheet(name, amount, currency):
    try:
        # កំណត់ Scope
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # ទាញយកសោសម្ងាត់ពី Streamlit Secrets (ដំណើរការលើ Cloud)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        
        # បើក Sheet ឈ្មោះ "Donation_List" (ត្រូវប្រាកដថាបាន Share ទៅ Email Service Account ហើយ)
        sheet = client.open("Donation_List").sheet1
        
        # យកម៉ោងបច្ចុប្បន្ន
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # បញ្ចូលទិន្នន័យ
        sheet.append_row([timestamp, name, amount, currency])
        return True
    except Exception as e:
        # បើមានបញ្ហា (ដូចជាអត់មាន Internet ឬរក Secrets មិនឃើញ)
        print(f"Sheet Error: {e}") 
        return False

# --- ២. មុខងារបង្កើតរូបភាព ---
def generate_appreciation_letter(name, amount_text):
    try:
        image = Image.open(TEMPLATE_FILE)
        draw = ImageDraw.Draw(image)
        
        # រក Font
        try:
            name_font = ImageFont.truetype(FONT_FILE, NAME_FONT_SIZE)
            amount_font = ImageFont.truetype(FONT_FILE, AMOUNT_FONT_SIZE)
        except:
            name_font = ImageFont.load_default()
            amount_font = ImageFont.load_default()
            
        W, H = image.size

        # --- សរសេរឈ្មោះ ---
        # ប្រើ try/except ដើម្បីការពារ Error លើ Windows (បញ្ហា libraqm)
        try:
            name_bbox = draw.textbbox((0, 0), name, font=name_font, language='km')
            name_w = name_bbox[2] - name_bbox[0]
            name_x = (W - name_w) / 2
            draw.text((name_x, NAME_Y_POS), name, font=name_font, fill=NAME_COLOR, language='km')

            # --- សរសេរទឹកប្រាក់ ---
            amount_bbox = draw.textbbox((0, 0), amount_text, font=amount_font, language='km')
            amount_w = amount_bbox[2] - amount_bbox[0]
            amount_x = (W - amount_w) / 2
            draw.text((amount_x, AMOUNT_Y_POS), amount_text, font=amount_font, fill=AMOUNT_COLOR, language='km')
        except KeyError:
            # Fallback សម្រាប់ Windows (អត់មាន language='km')
            name_bbox = draw.textbbox((0, 0), name, font=name_font)
            name_w = name_bbox[2] - name_bbox[0]
            name_x = (W - name_w) / 2
            draw.text((name_x, NAME_Y_POS), name, font=name_font, fill=NAME_COLOR)

            amount_bbox = draw.textbbox((0, 0), amount_text, font=amount_font)
            amount_w = amount_bbox[2] - amount_bbox[0]
            amount_x = (W - amount_w) / 2
            draw.text((amount_x, AMOUNT_Y_POS), amount_text, font=amount_font, fill=AMOUNT_COLOR)

        return image

    except FileNotFoundError:
        st.error("រកមិនឃើញឯកសាររូបភាព ឬ Font ទេ។ សូមពិនិត្យមើល Folder របស់អ្នក។")
        return None

# --- ផ្នែកបង្កើត User Interface ---
st.set_page_config(page_title="ICU Fundraising", page_icon="🏥")

st.title("🏥 មូលនិធិសាងសង់អគារ ICU")
st.subheader("ប្រព័ន្ធទទួលលិខិតថ្លែងអំណរគុណ")
st.write("សូមអរគុណចំពោះសមានចិត្តដ៏ថ្លៃថ្លារបស់លោកអ្នក។ សូមបំពេញព័ត៌មានខាងក្រោមដើម្បីទទួលលិខិត៖")

with st.form("donor_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        donor_name = st.text_input("ឈ្មោះសប្បុរសជន (ខ្មែរ/ឡាតាំង):", placeholder="ឧ. លោកឧកញ៉ា...")
    
    with col2:
        currency = st.selectbox("រូបិយប័ណ្ណ:", ["ដុល្លារ ($)", "រៀល (៛)"])
    
    amount_input = st.number_input("ចំនួនទឹកប្រាក់ដែលបានបរិច្ចាគ:", min_value=0.0, step=10.0, format="%.2f")
    
    submitted = st.form_submit_button("បរិច្ចាគ និងទទួលលិខិត")

if submitted:
    if not donor_name:
        st.warning("សូមបំពេញឈ្មោះសប្បុរសជន។")
    elif amount_input <= 0:
        st.warning("សូមបំពេញចំនួនទឹកប្រាក់។")
    else:
        # Format ទឹកប្រាក់
        if currency == "ដុល្លារ ($)":
            final_amount_text = f"{amount_input:,.2f} $" 
        else:
            final_amount_text = f"{int(amount_input):,} ៛" 
        
        with st.spinner('កំពុងរក្សាទុកទិន្នន័យ និងបង្កើតលិខិត...'):
            # ១. រក្សាទុកចូល Google Sheet
            is_saved = save_to_google_sheet(donor_name, amount_input, currency)
            
            # ២. បង្កើតរូបភាព
            result_img = generate_appreciation_letter(donor_name, final_amount_text)
            
            if result_img:
                if is_saved:
                    st.success("✅ ទិន្នន័យត្រូវបានរក្សាទុក និងបង្កើតលិខិតរួចរាល់!")
                else:
                    st.warning("⚠️ ទិន្នន័យមិនបាន Save ចូលបញ្ជីទេ (បញ្ហាអ៊ីនធឺណិត ឬ Secrets) ប៉ុន្តែលោកអ្នកនៅតែអាចយកលិខិតបាន។")
                
                st.image(result_img, caption="លិខិតថ្លែងអំណរគុណរបស់អ្នក", use_column_width=True)
                
                # ប៊ូតុង Download
                buf = io.BytesIO()
                result_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="⬇️ ទាញយកលិខិតថ្លែងអំណរគុណ (HQ)",
                    data=byte_im,
                    file_name=f"Appreciation_{donor_name}.png",
                    mime="image/png"
                )