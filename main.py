import uvicorn
from fastapi import FastAPI

# Para formatear
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Para instaciar la clase donde guardaremos la base de datos
from pydantic import BaseModel
# Añadir parametro de tipo query
from typing import Union,Optional
# Importamos nuestra base de datos
from constants import FAKE_DB_TOOLS

from fastapi import HTTPException

tool_list = list()
tool_list.extend(FAKE_DB_TOOLS)

class Tool(BaseModel):
    id: Optional[str] = None # Con esto indicamos que el parametro es opcional, para que pueda ser usando en elget y put
    name: str
    category: str

# CREAMOS UN METODO PARA LA BUSQUE DEL PARAMETRO
def find_index_by_id(tool_id):
    _index = None
    for index,value in enumerate(tool_list):
        if value["id"] == tool_id:
            _index = index
            break
    return _index
app = FastAPI()

# EJEMPLO USANDO QUERY PARAMS
@app.get(path="/api/tools/get_by_id", response_model=Tool)
async def get_tool_by_id(tool_id: Union[str, None] = None):
    if tool_id:
        response = list(filter(lambda x: x['id']== tool_id, tool_list))
        if not response:
            raise HTTPException(status_code=404, detail="No tools found for the given category")
    return JSONResponse(content=response, status_code=200)

# API GET PARA TODOS LAS HERRAMIENTAS
@app.get("/api/tools/get_all", response_model=Tool)
async def get_all_tools():
    status = 200
    response = tool_list
    return JSONResponse(content=response, status_code=status)

# EJEMPLO USANDO PATH PARAMS
@app.get(path="/api/tools/{tool_id}")
async def get_tool_by_id_2(tool_id:str):
    response = None
    status = 404
    for tool in tool_list:
        if tool['id'] == tool_id:
            response = tool
            status = 200
            break
    return JSONResponse(content=response, status_code=status)


@app.get(path="/api/tools/get_all_2")
async def get_tool_by_category(category: Union[str, None] = None):
    response = tool_list
    if category:
        response = list(filter(lambda x: x['category'].lower() == category.lower(), tool_list))
        if not response:
            raise HTTPException(status_code=404, detail="No tools found for the given category")
    return JSONResponse(content=response, status_code=200)

# Implementar un metodo POST que permita añadir una nueva herramienta
# Se necesita crear un modelo de datos, el cual ya ha sido creado como
# La clase Tool que deriva de BASEMODEL
# Se enviara como json
@app.post(path="/api/tools")
async def create_tool(tool: Tool):
    tool_id = tool.id
    if tool_id is None:
       tool.id = f'{tool.name}-{tool.category}'
    tool_list.append(tool.dict())
    json_data = jsonable_encoder(tool)
    return JSONResponse(content=json_data, status_code=201)

# Implementar un metodo PUT para actualizar una herramienta
@app.put(path="/api/tools/{tool_id}")
async def update_tool(tool_id: str, tool: Tool):
    if tool.id is None:
        tool.id = f'{tool.name}-{tool.category}'
    index_updated = find_index_by_id(tool_id=tool_id)
    if index_updated is None:
        return JSONResponse(content=None,status_code=404)
    else:
        tool_list[index_updated] = tool.dict()
    return  JSONResponse(content=True, status_code=200)


# Implementar un metodo DELETE para borrar una herramienta
@app.delete(path="/api/tools/{tool_id}")
async def delete_tool(tool_id: str):
    index_delete = find_index_by_id(tool_id=tool_id)
    if index_delete is None:
        return JSONResponse(content=None,status_code=404)
    else:
        tool_list.pop(index_delete)
        return JSONResponse(content=True, status_code=200)