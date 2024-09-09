import fitz  # PyMuPDF
import os
from req import encode_image_to_base64, generate_chat_response

def convert_image_to_text(image_pixmap):
    """Encodes the image from PDF page and generates text using OpenAI API."""
    with open('CODE/prompts/pdf_to_text/user_pdf_to_text.txt', 'r', encoding='utf-8') as user_file:
        user_prompt = user_file.read()
        
    with open('CODE/prompts/pdf_to_text/system_pdf_to_text.txt', 'r', encoding='utf-8') as system_file:
        system_prompt = system_file.read()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": user_prompt}, 
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image_to_base64(image_pixmap)}"}}
            ]
        }
    ]
    return generate_chat_response(messages, 4096)


def extract_text_from_pdf(pdf_file_path):
    """Extracts text from a PDF file using image-to-text conversion for each page."""
    pdf_document = fitz.open(pdf_file_path)
    extracted_text = ''
    for page_number in range(pdf_document.page_count):
        print(f'Processing page {page_number + 1} of {pdf_document.page_count}')
        page = pdf_document.load_page(page_number)
        pixmap = page.get_pixmap()
        extracted_text += convert_image_to_text(pixmap)
    pdf_document.close()

    return extracted_text


def generate_lecture_text(level_number, language, article_text):
    """Generates a lecture text based on article text and prompts."""
    print('Generating lecture text based on the article...')
    with open(f'CODE/prompts/lectures/levels/{level_number}_level.txt', 'r', encoding='utf-8') as level_file:
        detail_level = level_file.read()
        
    with open(f'CODE/prompts/lectures/user_text_to_lecture.txt', 'r', encoding='utf-8') as user_file:
        user_prompt = user_file.read().replace('{detail_level}', detail_level).replace('{language}', language).replace('{article_text}', article_text)
        
    with open(f'CODE/prompts/lectures/system_text_to_lecture.txt', 'r', encoding='utf-8') as system_file:
        system_prompt = system_file.read()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return generate_chat_response(messages, 4096)


def generate_podcast_text(level_number, language, article_text):
    """Generates a podcast text based on article text and prompts."""
    print('Generating podcast text based on the article...')
    with open(f'CODE/prompts/podcast/levels/{level_number}_level.txt', 'r', encoding='utf-8') as level_file:
        detail_level = level_file.read()
        
    with open(f'CODE/prompts/podcast/user_text_to_podcast.txt', 'r', encoding='utf-8') as user_file:
        user_prompt = user_file.read().replace('{detail_level}', detail_level).replace('{language}', language).replace('{article_text}', article_text)
        
    with open(f'CODE/prompts/podcast/system_text_to_podcast.txt', 'r', encoding='utf-8') as system_file:
        system_prompt = system_file.read()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return generate_chat_response(messages, 4096)


def generate_audio_from_text(text, output_path):
    """Generates an audio file from the lecture text using OpenAI API."""
    print('Generating audio from the lecture text...')
    
    # Use OpenAI API to convert text to speech (you need to adapt this part with correct API call)
    audio_response = generate_chat_response([{"role": "user", "content": text}], 4096)  # Mock response for simplicity
    
    audio_file_path = os.path.join(output_path, 'lecture_audio.mp3')
    
    # Save the generated audio to the file
    with open(audio_file_path, 'wb') as audio_file:
        audio_file.write(audio_response.encode('utf-8'))  # Mock binary writing; you need real audio handling here
    
    print(f'Successfully saved audio to {audio_file_path}')


def main():
    """Main function to process input files and generate output based on settings."""
    # Step 1: Read settings from file
    with open('settings.txt', 'r', encoding='utf-8') as settings_file:
        settings = settings_file.read().strip().split('\n')
    
    language = settings[0].split('=')[1].strip().strip('"')
    output_format = settings[1].split('=')[1].strip().strip('"')
    detail_level = int(settings[2].split('=')[1].strip())

    # Step 2: Process files from input directory
    input_dir = 'input'
    output_dir = 'output'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        
        # Check if the file is a PDF or TXT
        if file_name.endswith('.pdf'):
            print(f'Processing PDF file: {file_name}')
            article_text = extract_text_from_pdf(file_path)
        elif file_name.endswith('.txt'):
            print(f'Processing TXT file: {file_name}')
            with open(file_path, 'r', encoding='utf-8') as text_file:
                article_text = text_file.read()
        else:
            print(f'Skipping unsupported file format: {file_name}')
            continue
        
        # Step 3: Create an output folder per file
        base_name = os.path.splitext(file_name)[0]  # Remove file extension
        file_output_dir = os.path.join(output_dir, f'{base_name}_{output_format}')
        
        if not os.path.exists(file_output_dir):
            os.makedirs(file_output_dir)
        
        # Step 4: Generate content based on settings
        if output_format == 'lecture':
            generated_text = generate_lecture_text(detail_level, language, article_text)
            output_file_name = f"{base_name}_lecture.txt"
            output_file_path = os.path.join(file_output_dir, output_file_name)
            
            # Save generated text
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(generated_text)
            
            print(f'Successfully generated {output_file_name}')
            
            # Generate audio for lecture
            generate_audio_from_text(generated_text, file_output_dir)
        
        elif output_format == 'podcast':
            generated_text = generate_podcast_text(detail_level, language, article_text)
            output_file_name = f"{base_name}_podcast.txt"
            output_file_path = os.path.join(file_output_dir, output_file_name)
            
            # Save generated text
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(generated_text)
            
            print(f'Successfully generated {output_file_name}')
        else:
            print(f'Unknown output format: {output_format}')
            continue


if __name__ == "__main__":
    main()
