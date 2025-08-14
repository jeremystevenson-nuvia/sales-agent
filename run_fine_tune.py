from dotenv import load_dotenv
load_dotenv()

from finetune.fine_tune_model import GPT4FineTuner

"""Main function to run the fine-tuning process"""
try:
    fine_tuner = GPT4FineTuner()
    fine_tuner.run_fine_tuning_pipeline()
except Exception as e:
    print(f"Failed to run fine-tuning: {e}")


