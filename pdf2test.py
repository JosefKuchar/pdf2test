from pypdf import PdfReader
import os
from dotenv import load_dotenv
import google.generativeai as genai
from argparse import ArgumentParser
import glob
import json
from tqdm import tqdm
from string import Template


def parse_args():
    """Parse arguments"""

    parser = ArgumentParser(description="Convert PDF to drill file")
    # Path to folder with files
    parser.add_argument("path", help="Path to folder with PDF files")
    parser.add_argument("--template", help="Template file", default="templates/cs.txt")
    parser.add_argument("--output", help="Output file")
    return parser.parse_args()


def generate_qa(args):
    """Generate questions and answers"""

    # Configure gemini
    genai.configure(api_key=os.getenv("KEY"))
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    # Get list of files in folder recursively
    files = glob.glob(args.path + "/**/*.pdf", recursive=True)

    questions = []
    with open(args.template, "r", encoding="utf-8") as template:
        template = template.read()
        with open(args.output, "w") as f:
            # Iterate over files
            for file in tqdm(files):
                # Get text from PDF
                reader = PdfReader(file)
                text = "\n".join([page.extract_text() for page in reader.pages])

                while True:
                    try:
                        # Create prompt
                        prompt = Template(template).substitute({"slides": text})

                        # Generate questions
                        response = model.generate_content(
                            prompt,
                            generation_config=genai.GenerationConfig(
                                response_mime_type="application/json"
                            ),
                        )

                        res = response.text
                        data = None
                        # Autofix JSON
                        while True:
                            if not res:
                                raise ValueError("Couldn't fix JSON")
                            try:
                                data = json.loads(res + "]")
                            except json.decoder.JSONDecodeError:
                                res = res[:-1]
                                continue
                            break

                        valid = []
                        # Check valid questions
                        for q in data:
                            if "correct" in q and len(q["correct"]) > 0:
                                valid.append(q)

                        # Check if there are any valid questions
                        if len(valid) == 0:
                            print(f"{file} No valid questions, retrying ...")
                            continue

                        # Append questions to list
                        print(
                            f"Extending with {len(valid)} questions ({len(data)} total)"
                        )
                        questions.extend(valid)
                        break
                    except Exception as e:
                        print(e)
                        print(f"{file} Error, trying again ...")
                        continue

            # Write questions to file
            json.dump(questions, f)


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Parse arguments and generate
    generate_qa(parse_args())
