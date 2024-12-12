# First you will have to set a global environment variable called OPENAI_API_KEY
# export OPENAI_API_KEY='KEY'


import os

from biochatter.api_agent import AnnDataIOQueryBuilder, format_as_python_call
from biochatter.llm_connect import GptConversation


def conversation():
    """Set up a real GptConversation instance."""
    prompts = {
        "primary_model_prompts": [
            "You are an AI specialized in answering AnnData-related queries.",
        ],
        "correcting_agent_prompts": [],
        "tool_prompts": {},
        "rag_agent_prompts": [],
    }
    # Create GptConversation instance
    convo = GptConversation(
        model_name="gpt-4",  # Replace with your preferred model
        prompts=prompts,
        correct=False,
        split_correction=False,
    )
    # Set the API key (ensure the key is set in the environment)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set!")
    success = convo.set_api_key(api_key=api_key, user="test_user")
    if not success:
        raise ValueError("Failed to set the API key or initialize the LLM connection!")
    return convo


def test_querybuilder_with_real_conversation(conversation):
    """Test the AnnDataIOQueryBuilder with a real LLM API."""
    # Define the query builder
    query_builder = AnnDataIOQueryBuilder()
    # Example question
    question = "How do I read an test.h5ad file using AnnData?"
    # Parameterize the query
    result = query_builder.parameterise_query(
        question=question,
        conversation=conversation,
    )
    # Print results for debugging
    print("\nStructured Output:\n", result)
    xx = format_as_python_call(result[0])
    print("\nThe formatted python call is: \n", xx)


# Run the test
if __name__ == "__main__":
    convo = conversation()
    test_querybuilder_with_real_conversation(convo)
    print("Test completed.")
