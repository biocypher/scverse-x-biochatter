from pydantic import Field, create_model, BaseModel, ConfigDict
from typing import Optional
# To include the uuid we need to modify the BaseModel template
class BaseAPIModel(BaseModel):
    """A base class for all API models.

    Adds 'uuid' to default fields.
    """
    #model_extra: dict[str, str] = {"uuid": "some-unique-identifier"}
    uuid: str | None = Field(
        None, description="Unique identifier for the model instance"
    )
    # Another option to add the uuid without modifying the actual output schema. Still not entirely sure how to do this
    # https://docs.pydantic.dev/2.10/api/base_model/#pydantic.BaseModel
    model_config = ConfigDict(arbitrary_types_allowed=True)#, extra="allow")

        



# As a direct template as input for the create_model function, one could directly define the fields dictionary which contains fields
# Create one dictionary for all descriptions and one for all parameters. The keys are the function names and need to match

tool_params = {}
tool_descriptions = {}

tool_name = "read_h5ad"
tool_descriptions[tool_name] = "Function to read h5ad files. Available in the anndata.io module"
tool_params[tool_name] = {
    "filename": (str, Field(default="dummy.h5ad", description="Path to the .h5ad file")),
    "backed": (Optional[str], Field(default=None, description="Mode to access file: None, 'r' for read-only")),
    "as_sparse": (Optional[str], Field(default=None, description="Convert to sparse format: 'csr', 'csc', or None")),
    "as_sparse_fmt": (Optional[str], Field(default=None, description="Sparse format if converting, e.g., 'csr'")),
    "index_unique": (Optional[str], Field(default=None, description="Make index unique by appending suffix if needed"))
}

tool_name = "read_zarr" 
tool_descriptions[tool_name] = "Function to read Zarr stores. Available in the anndata.io module"
tool_params[tool_name] = {
    "filename": (str, Field(default="placeholder.zarr", description="Path or URL to the Zarr store"))
}

def create_model_from_template(tool_params, tool_descriptions):
    tools = []
    # validate that keys are equal in tool_params and tool_descriptions
    if not set(tool_params.keys()) == set(tool_descriptions.keys()):
        raise ValueError("Keys in tool_params and tool_descriptions must be equal")
    for tool_name in tool_descriptions.keys():
        parameters = tool_params[tool_name]
        tool_description = tool_descriptions[tool_name]
        tools.append(create_model(tool_name, __doc__=tool_description, **parameters, __base__=BaseAPIModel))
    return tools

tools = create_model_from_template(tool_params, tool_descriptions)

#check if it can be passed to the llm
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticToolsParser
from typing import Any

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm_with_tools = llm.bind_tools(tools, tool_choice=True)
chain = llm_with_tools | PydanticToolsParser(tools=tools)
query = [
	("system", "You're a helpful assistant that parameterizes function calls"), 
	("human", "I want to read a h5ad file"),
]
result = chain.invoke(query)
print(result)
