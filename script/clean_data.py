import os
import re

def clean_text(text):
    pattern = re.compile(r'[^a-zA-Z0-9\s]')
    cleaned_text = re.sub(pattern, '', text)
    cleaned_text = '\n'.join(line for line in cleaned_text.splitlines() if line.strip())
    return cleaned_text

def main():
    input_folder = '../../documents/PHARM/text/'  
    output_folder = './PHARM/cleaned_text/'  

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):  
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, f'cleaned_{filename}')

            try:
                with open(input_file, 'r', encoding='utf-8') as file:
                    text = file.read()
                    cleaned_text = clean_text(text)

                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(cleaned_text)

                print(f'Cleaned text saved to {output_file}')

            except FileNotFoundError:
                print(f'Error: File "{input_file}" not found.')

if __name__ == "__main__":
    main()
