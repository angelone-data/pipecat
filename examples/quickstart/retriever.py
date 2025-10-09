
import os
# from openai import OpenAIChatModel, OpenAIProvider
from langchain_aws import AmazonKnowledgeBasesRetriever
from dotenv import load_dotenv 
from chatbot.constant import retrieved_doc_no
load_dotenv() 
query = "Hi whats the process to open a demat account in angelone?"

class Retriever:
        def __init__(self):
            self.kb_region_name = os.environ["KB_AWS_REGION"]
            self.kb_id = os.environ["KNOWLEDGE_BASE_ID"]
            self.number_of_results = retrieved_doc_no

        @staticmethod
        def create_retriever(kb_region_name, kb_id, retrieved_doc_no):
                retrieval_config = {
                    "vectorSearchConfiguration": {
                        "numberOfResults": retrieved_doc_no,
                    }
                }

                retriever = AmazonKnowledgeBasesRetriever(
                    knowledge_base_id=kb_id,
                    retrieval_config=retrieval_config,
                    region_name=kb_region_name,
                )
                return retriever
        
        def retrieved_doc(self, query):
                retriever = self.create_retriever(self.kb_region_name, self.kb_id, self.number_of_results)
                docs = retriever.invoke(query)
                return docs
        
        def retrieved_content_list(self, query):
                docs = self.retrieved_doc(query)
                doc_content_list = [doc.page_content for doc in docs]
                return doc_content_list
               
        def retrieved_content_string(self, query):
                doc_content_list = self.retrieved_content_list(query)
                retrieved_doc =  "Doc 1 :"+ "Doc 2 : ".join(doc_content_list)
                return retrieved_doc
        

               
        





