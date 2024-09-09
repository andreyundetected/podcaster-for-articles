import fitz  # PyMuPDF
import os
from req import encode_image_to_base64, generate_chat_response, generate_audio


# Function that takes an image from a PDF page, sends it to the OpenAI API, and returns the generated text.
def convert_image_to_text(image_pixmap):
    with open('CODE/prompts/pdf_to_text/user_pdf_to_text.txt', 'r', encoding='utf-8') as user_file:
        user_prompt = user_file.read()

    with open('CODE/prompts/pdf_to_text/system_pdf_to_text.txt', 'r', encoding='utf-8') as system_file:
        system_prompt = system_file.read()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "text", "text": user_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image_to_base64(image_pixmap)}"}}
        ]}
    ]
    return generate_chat_response(messages, 4096)


# Function that processes a PDF file, extracts text from each page, and returns the full extracted text.
def extract_text_from_pdf(pdf_file_path):
    pdf_document = fitz.open(pdf_file_path)
    extracted_text = ''

    for page_number in range(pdf_document.page_count):
        print(f'    Processing page {page_number + 1} of {pdf_document.page_count}')
        page = pdf_document.load_page(page_number)
        pixmap = page.get_pixmap()
        extracted_text += convert_image_to_text(pixmap)

    pdf_document.close()
    return extracted_text


# Function that generates a lecture based on prompts and the provided article text, returns generated text.
def generate_lecture_text(level_number, language, article_text):
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


# Function that generates podcast text based on prompts and article text, returns generated text.
def generate_podcast_text(level_number, language, article_text):
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


# Main function that processes input files and generates either lectures or podcasts based on settings.
def main():
    with open('settings.txt', 'r', encoding='utf-8') as settings_file:
        settings = settings_file.read().strip().split('\n')

    language = settings[0].split('=')[1].strip().strip('"')
    output_format = settings[1].split('=')[1].strip().strip('"')
    detail_level = int(settings[2].split('=')[1].strip())

    input_dir = 'input'
    output_dir = 'output'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)

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

        base_name = os.path.splitext(file_name)[0]
        file_output_dir = os.path.join(output_dir, f'{base_name}_{output_format}')

        if not os.path.exists(file_output_dir):
            os.makedirs(file_output_dir)

        if output_format == 'lecture':
            generated_text = generate_lecture_text(detail_level, language, article_text)
            output_file_name = f"{base_name}_lecture"
            output_file_path = os.path.join(file_output_dir, output_file_name)

            with open(f"{output_file_path}.txt", 'w', encoding='utf-8') as output_file:
                output_file.write(generated_text)

            print('Generating an audio lecture...')
            audio_content = generate_audio(generated_text, voice='fable')
            with open(f"{output_file_path}.mp3", 'wb') as audio_file:
                audio_file.write(audio_content)

            print(f'Successfully generated {output_file_name}')

        elif output_format == 'podcast':
            generated_text = generate_podcast_text(detail_level, language, article_text)
            output_file_name = f"{base_name}_podcast"
            output_file_path = os.path.join(file_output_dir, output_file_name)

            print('Generating podcast audio...')
            audio_content = b''
            l = len(generated_text.split('\nQ:'))
            for i, two_phrases in enumerate(generated_text.split('\nQ:')):
                print(f"    Processing phrase {i + 1} of {l}")
                Q_text = two_phrases.split('\nA:')[0]
                audio_content += generate_audio(Q_text, voice='fable')

                if len(two_phrases.split('\nA:')) > 1:
                    A_text = two_phrases.split('\nA:')[1]
                    audio_content += generate_audio(A_text, voice='nova')

            with open(f"{output_file_path}.mp3", 'wb') as audio_file:
                audio_file.write(audio_content)

            with open(f"{output_file_path}.txt", 'w', encoding='utf-8') as output_file:
                output_file.write(generated_text)

            print(f'Successfully generated {output_file_name}')
        else:
            print(f'Unknown output format: {output_format}')
            continue


if __name__ == "__main__":
    main()
