import streamlit as st
import boto3
import json
import base64
import io
from PIL import Image
import os
import datetime
import time
import subprocess
import re
import pywhatkit

# Page configuration
st.set_page_config(
    page_title="WhatsApp Image Sender",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Session state initialization
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'current_image_path' not in st.session_state:
    st.session_state.current_image_path = None
if 'images_folder' not in st.session_state:
    st.session_state.images_folder = os.path.join(os.getcwd(), "generated_images")
    os.makedirs(st.session_state.images_folder, exist_ok=True)
if 'show_whatsapp_warning' not in st.session_state:
    st.session_state.show_whatsapp_warning = False
    
# Sidebar
with st.sidebar:
    # Logo
    st.image("shellkode.jpeg", width=150)
    
    st.markdown("### Links")
    st.markdown("[🔗 GitHub Repository](https://github.com/shellkodelabs/personalized-whatapp-wish)")
    st.markdown("[👤 LinkedIn](https://www.linkedin.com/company/shellkode/)")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app generates custom New Year 2025 images
    and helps you share them via WhatsApp.
    
    Built with ❤️ by ShellKode
    """)

# Helper functions
@st.cache_resource
def get_bedrock_client():
    return boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2'
    )

def generate_image(name, prompt):
    try:
        bedrock = get_bedrock_client()
        personalized_prompt = prompt.replace("Happy New Year 2025", f"Happy New Year 2025 {name}")
        
        request = json.dumps({"prompt": personalized_prompt})
        response = bedrock.invoke_model(
            body=request,
            modelId='stability.stable-image-ultra-v1:1',
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        base64_image = response_body["images"][0]
        image_data = base64.b64decode(base64_image)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"newyear2025_{timestamp}.jpg"
        image_path = os.path.join(st.session_state.images_folder, image_filename)
        
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        image.save(image_path, "JPEG", quality=95)
        
        return image_path, image
        
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None, None

def copy_image_to_clipboard(image_path):
    try:
        absolute_path = os.path.abspath(image_path)
        cmd = f'''
        osascript -e '
        set theFile to POSIX file "{absolute_path}"
        set theImage to (read theFile as JPEG picture)
        set the clipboard to theImage
        '
        '''
        subprocess.run(cmd, shell=True, check=True)
        return True
    except Exception as e:
        st.error(f"Error copying image to clipboard: {str(e)}")
        return False

def clean_phone_number(number):
    cleaned = re.sub(r'[^0-9]', '', str(number))
    if len(cleaned) == 11 and cleaned.startswith('1'):
        return '+' + cleaned
    elif len(cleaned) == 10:
        return '+91' + cleaned
    elif len(cleaned) > 10:
        return '+' + cleaned
    else:
        raise ValueError(f"Invalid phone number format: {number}")

def send_whatsapp_message(phone, image_path):
    try:
        formatted_number = clean_phone_number(phone)
        pywhatkit.sendwhats_image(
            receiver=formatted_number,
            img_path=image_path,
            caption="Happy New Year 2025! 🎊",
            wait_time=30,
            tab_close=True
        )
        time.sleep(20)
        return True
            
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return False

# Main content
def main():
    # Create two columns for main layout
    main_col1, main_col2 = st.columns([2, 1])
    
    with main_col1:
        st.title("🎉 New Year Magic: Personalized Greetings Generator ✨")
        
        # Contact details in a card-like container
        with st.expander("👤 Contact Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", placeholder="Enter name")
            with col2:
                phone = st.text_input("Phone", placeholder="+91XXXXXXXXXX")
        
        # Theme selection
        st.markdown("### 🎨 Select Theme")
        themes = {
            "Snow, Gifts, and Trees": {
                "preview": "theme1.jpeg",
                "prompt": """A festive winter scene with a cozy cabin in the background surrounded by snow-covered pine trees. The foreground features a stack of colorful, intricately wrapped gifts glowing softly under the moonlight. Twinkling fairy lights are draped across the trees, and a cheerful snowman wearing a scarf and hat stands beside a wooden sign that says 'Happy New Year 2025' in elegant, frosted letters. The sky above is filled with gently falling snowflakes and a brilliant aurora borealis."""
            },
            "Fantastical Creatures": {
                "preview": "theme2.jpeg",
                "prompt": """An enchanted forest illuminated by bioluminescent plants and glowing mushrooms. Mystical creatures like fairies, unicorns, and forest spirits are gathered in a circle celebrating the New Year. A large magical tree in the center has 'Happy New Year 2025' written in golden glowing letters on its trunk. The atmosphere is vibrant, with shimmering sparkles, colorful lanterns hanging from the branches, and fantastical lights creating a whimsical, dreamlike environment."""
            },
            "Nature Snow with Stars": {
                "preview": "theme3.jpeg",
                "prompt": """A tranquil snowy landscape under a crystal-clear night sky filled with stars and a radiant Milky Way. Snow-covered hills stretch into the distance, and a lone frozen lake reflects the celestial display above. The scene is adorned with twinkling frost-covered trees, and the words 'Happy New Year 2025' are written in the snow, glowing with a soft golden hue. Shooting stars streak across the sky, adding a touch of magic to the serene and peaceful setting."""
            },
            "Custom": {
                
                "prompt": ""
            }
        }
        
        selected_theme = st.radio("Choose theme", list(themes.keys()), horizontal=True)
        
        # Theme previews in a grid
        if selected_theme != "Custom":
            preview_cols = st.columns(3)
            for i, (theme, theme_data) in enumerate(themes.items()):
                if theme != "Custom":
                    with preview_cols[i]:
                        st.image(theme_data["preview"], caption=theme, use_column_width=True)
        
        # Custom prompt section
        custom_prompt = ""
        if selected_theme == "Custom":
            st.markdown("### ✍️ Custom Prompt")
            custom_prompt = st.text_area(
                "Enter your custom prompt",
                height=150,
                placeholder="Describe the image you want to generate. Be specific and detailed about the scene, colors, mood, and elements you want to include. Don't forget to mention 'Happy New Year 2025' somewhere in your prompt.",
                help="Your prompt should be detailed and descriptive. The better the prompt, the better the generated image."
            )
            
            with st.expander("📝 Example Prompts"):
                st.markdown("""
                Here are some example prompts you can use as inspiration:
                
                1. "A futuristic cityscape at midnight with floating holographic '2025' numbers, flying cars, and neon lights reflecting off glass buildings. Happy New Year 2025 written in sparkling digital letters across the sky."
                
                2. "A magical underwater scene with bioluminescent sea creatures, coral reefs glowing in rainbow colors, and marine life celebrating the new year. 'Happy New Year 2025' formed by shimmering bubbles rising to the surface."
                
                3. "A cozy coffee shop interior decorated for New Year, with fairy lights, vintage decorations, and a steaming cup of coffee with '2025' forming in the steam. A chalkboard in the background displays 'Happy New Year' in artistic lettering."
                """)
        
        # Generate button
        if st.button("🎨 Generate Image", use_container_width=True):
            if not name or not phone:
                st.error("Please enter both name and phone number")
                return
            
            if selected_theme == "Custom" and not custom_prompt:
                st.error("Please enter a custom prompt")
                return
                
            with st.spinner('✨ Creating your image...'):
                prompt = custom_prompt if selected_theme == "Custom" else themes[selected_theme]["prompt"]
                image_path, image = generate_image(name, prompt)
                if image_path and image:
                    st.session_state.current_image = image
                    st.session_state.current_image_path = image_path
    
    with main_col2:
        # Display generated image and actions
        if st.session_state.current_image is not None:
            st.markdown("### 🖼️ Preview")
            st.image(st.session_state.current_image, use_column_width=True)
            
            # Action buttons
            st.download_button(
                "📥 Download",
                data=open(st.session_state.current_image_path, "rb"),
                file_name="newyear2025.jpg",
                mime="image/jpeg",
                use_container_width=True
            )
            
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                if copy_image_to_clipboard(st.session_state.current_image_path):
                    st.success("✅ Copied!")
                else:
                    st.error("❌ Failed")
            
            if st.button("📱 Send via WhatsApp", use_container_width=True):
                st.session_state.show_whatsapp_warning = True
            
            # WhatsApp warning
            if st.session_state.show_whatsapp_warning:
                with st.expander("⚠️ Important Information", expanded=True):
                    st.warning("""
                    - WhatsApp Web will open in a new tab
                    - Process takes ~40 seconds
                    - Don't change tabs during process
                    - Image will be copied to clipboard
                    """)
                    
                    if st.button("✅ Continue to WhatsApp", use_container_width=True):
                        if send_whatsapp_message(phone, st.session_state.current_image_path):
                            st.success("✅ WhatsApp opened! Paste image with Ctrl/Cmd+V")
                            st.session_state.show_whatsapp_warning = False
                        else:
                            st.error("❌ Failed to open WhatsApp")

if __name__ == "__main__":
    main()