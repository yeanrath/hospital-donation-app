import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- ផ្នែកកំណត់ការកំណត់ (Configuration) ---
# សូមកែសម្រួលលេខកូដទីតាំងខាងក្រោម ឱ្យត្រូវនឹងរូបភាព Template របស់អ្នក
TEMPLATE_FILE = "appreciation_template.png"
FONT_FILE = "KhmerOSmuollight.ttf"

# កំណត់ទីតាំង និងទំហំអក្សរ (លោកអ្នកត្រូវសាកល្បងកែលេខនេះជាក់ស្តែង)
NAME_FONT_SIZE = 50
NAME_Y_POS = 780      # កម្ពស់សម្រាប់ដាក់ "ឈ្មោះសប្បុរសជន"
NAME_COLOR = (50, 89, 158) # ពណ៌ទឹកប៊ិច
AMOUNT_FONT_SIZE = 50
AMOUNT_Y_POS = 850     # កម្ពស់សម្រាប់ដាក់ "ចំនួនទឹកប្រាក់"
AMOUNT_COLOR = (192, 57, 43) # ពណ៌ក្រហម (ដើម្បីឱ្យលេចធ្លោ)

def generate_appreciation_letter(name, amount_text):
    try:
        image = Image.open(TEMPLATE_FILE)
        draw = ImageDraw.Draw(image)
        
        # --- ១. សរសេរឈ្មោះ (ដាក់កណ្តាល) ---
        try:
            name_font = ImageFont.truetype(FONT_FILE, NAME_FONT_SIZE)
        except:
            name_font = ImageFont.load_default()
            
        W, H = image.size
        # គណនាប្រវែងអក្សរឈ្មោះ ដើម្បីដាក់ឱ្យចំកណ្តាលរូប
        name_bbox = draw.textbbox((0, 0), name, font=name_font)
        name_w = name_bbox[2] - name_bbox[0]
        name_x = (W - name_w) / 2
        
        draw.text((name_x, NAME_Y_POS), name, font=name_font, fill=NAME_COLOR, language='km')

        # --- ២. សរសេរចំនួនទឹកប្រាក់ (ដាក់កណ្តាលដូចគ្នា) ---
        amount_font = ImageFont.truetype(FONT_FILE, AMOUNT_FONT_SIZE)
        
        amount_bbox = draw.textbbox((0, 0), amount_text, font=amount_font)
        amount_w = amount_bbox[2] - amount_bbox[0]
        amount_x = (W - amount_w) / 2
        
        draw.text((amount_x, AMOUNT_Y_POS), amount_text, font=amount_font, fill=AMOUNT_COLOR, language='km')

        return image

    except FileNotFoundError:
        st.error("រកមិនឃើញឯកសាររូបភាព ឬ Font ទេ។ សូមពិនិត្យមើល Folder របស់អ្នក។")
        return None

# --- ផ្នែកបង្កើត User Interface ---
st.set_page_config(page_title="ICU Fundraising", page_icon="🏥")

st.title("🏥 មូលនិធិសាងសង់អគារ ICU")
st.subheader("ប្រព័ន្ធទទួលលិខិតថ្លែងអំណរគុណ")
st.write("សូមអរគុណចំពោះសមានចិត្តដ៏ថ្លៃថ្លារបស់លោកអ្នក។ សូមបំពេញព័ត៌មានខាងក្រោមដើម្បីទទួលលិខិត៖")

# ហ្វ form បញ្ចូលទិន្នន័យ
with st.form("donor_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        donor_name = st.text_input("ឈ្មោះសប្បុរសជន (ខ្មែរ/ឡាតាំង):", placeholder="ឧ. លោកឧកញ៉ា...")
    
    with col2:
        currency = st.selectbox("រូបិយប័ណ្ណ:", ["ដុល្លារ ($)", "រៀល (៛)"])
    
    amount_input = st.number_input("ចំនួនទឹកប្រាក់ដែលបានបរិច្ចាគ:", min_value=0.0, step=10.0, format="%.2f")
    
    submitted = st.form_submit_button("បង្កើតលិខិតថ្លែងអំណរគុណ")

if submitted and donor_name and amount_input > 0:
    # Format ទឹកប្រាក់ (ឧទាហរណ៍: 1,000 $)
    if currency == "ដុល្លារ ($)":
        final_amount_text = f"{amount_input:,.2f} $" # ដាក់ក្បៀស និងសញ្ញាដុល្លារ
    else:
        final_amount_text = f"{int(amount_input):,} ៛" # ដាក់ក្បៀស និងសញ្ញារៀល
        
    st.info(f"កំពុងបង្កើតលិខិតជូន៖ {donor_name} ចំនួន {final_amount_text}...")
    
    # ហៅ Function បង្កើតរូបភាព
    result_img = generate_appreciation_letter(donor_name, final_amount_text)
    
    if result_img:
        st.success("រួចរាល់! សូមត្រួតពិនិត្យ និង Download ខាងក្រោម៖")
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
elif submitted:
    st.warning("សូមបំពេញឈ្មោះ និងចំនួនទឹកប្រាក់ឱ្យបានត្រឹមត្រូវ។")