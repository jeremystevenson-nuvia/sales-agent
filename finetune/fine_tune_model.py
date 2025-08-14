#!/usr/bin/env python3
"""
GPT-4 Fine-tuning Script using LangChain and OpenAI
This script processes documents and creates fine-tuning data for GPT-4
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any
# from dotenv import load_dotenv
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import tiktoken
from finetune import config

# Load environment variables
# load_dotenv()

class GPT4FineTuner:
    def __init__(self):
        """Initialize the fine-tuner with OpenAI client"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.client = OpenAI(api_key=self.api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=self.num_tokens_from_string,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def num_tokens_from_string(self, string: str, encoding_name: str = "cl100k_base") -> int:
        """Count the number of tokens in a string"""
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens
    
    def load_documents(self, docs_dir: str = config.DOCS_DIRECTORY) -> List[Document]:
        """Load all documents from the docs directory"""
        documents = []
        docs_path = Path(docs_dir)
        
        if not docs_path.exists():
            raise FileNotFoundError(f"Directory {docs_dir} not found")
        
        # Load text files
        for txt_file in docs_path.glob("*.txt"):
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append(Document(
                    page_content=content,
                    metadata={"source": str(txt_file), "type": "text"}
                ))
        
        # Load markdown files
        for md_file in docs_path.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append(Document(
                    page_content=content,
                    metadata={"source": str(md_file), "type": "markdown"}
                ))
        
        print(f"Loaded {len(documents)} documents")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks for fine-tuning"""
        split_docs = self.text_splitter.split_documents(documents)
        print(f"Split documents into {len(split_docs)} chunks")
        return split_docs
    
    def create_fine_tuning_data(self, documents: List[Document], output_file: str = config.TRAINING_DATA_FILE) -> str:
        """Create fine-tuning data in JSONL format"""
        training_data = []
        
        for i, doc in enumerate(documents):
            # Create a simple instruction-following format
            instruction = f"Please analyze and respond to the following content from {doc.metadata['source']}:"
            content = doc.page_content
            
            # Create training example
            training_example = {
                "messages": [
                    {"role": "system", "content": config.SYSTEM_PROMPT},
                    {"role": "user", "content": f"{instruction}\n\n{content}"},
                    {"role": "assistant", "content": f"I've analyzed the content from {doc.metadata['source']}. This document contains: {content[:200]}..."}
                ]
            }
            
            training_data.append(training_example)
        
        # Write to JSONL file
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in training_data:
                f.write(json.dumps(example) + '\n')
        
        print(f"Created fine-tuning data file: {output_file}")
        print(f"Total training examples: {len(training_data)}")
        return output_file
    
    def upload_training_file(self, file_path: str) -> str:
        """Upload the training file to OpenAI"""
        try:
            with open(file_path, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose="fine-tune"
                )
            print(f"Uploaded training file. File ID: {response.id}")
            return response.id
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise
    
    def create_fine_tuning_job(self, training_file_id: str, model: str = config.OPENAI_MODEL) -> str:
        """Create a fine-tuning job"""
        try:
            response = self.client.fine_tuning.jobs.create(
                training_file=training_file_id,
                model=model
            )
            print(f"Created fine-tuning job. Job ID: {response.id}")
            print(f"Status: {response.status}")
            return response.id
        except Exception as e:
            print(f"Error creating fine-tuning job: {e}")
            raise
    
    def monitor_fine_tuning_job(self, job_id: str):
        """Monitor the progress of a fine-tuning job"""
        print(f"Monitoring fine-tuning job: {job_id}")
        
        while True:
            try:
                job = self.client.fine_tuning.jobs.retrieve(job_id)
                print(f"Status: {job.status}")
                
                if job.status in ["succeeded", "failed", "cancelled"]:
                    if job.status == "succeeded":
                        print(f"Fine-tuning completed! Model: {job.fine_tuned_model}")
                    elif job.status == "failed":
                        print(f"Fine-tuning failed: {job.error}")
                    elif job.status == "cancelled":
                        print("Fine-tuning was cancelled")
                    break
                
                # Wait before checking again
                import time
                time.sleep(config.MONITORING_INTERVAL)  # Check every minute
                
            except Exception as e:
                print(f"Error monitoring job: {e}")
                break
    
    def run_fine_tuning_pipeline(self):
        """Run the complete fine-tuning pipeline"""
        print("Starting GPT-4 fine-tuning pipeline...")
        
        try:
            # Step 1: Load documents
            print("\n1. Loading documents...")
            documents = self.load_documents()
            
            # Step 2: Split documents
            print("\n2. Splitting documents...")
            split_docs = self.split_documents(documents)
            
            # Step 3: Create training data
            print("\n3. Creating training data...")
            training_file = self.create_fine_tuning_data(split_docs)
            
            # Step 4: Upload training file
            print("\n4. Uploading training file...")
            file_id = self.upload_training_file(training_file)
            
            # Step 5: Create fine-tuning job
            print("\n5. Creating fine-tuning job...")
            job_id = self.create_fine_tuning_job(file_id)
            
            # Step 6: Monitor progress
            print("\n6. Monitoring fine-tuning progress...")
            self.monitor_fine_tuning_job(job_id)
            
            print("\nFine-tuning pipeline completed!")
            
        except Exception as e:
            print(f"Error in fine-tuning pipeline: {e}")
            raise

