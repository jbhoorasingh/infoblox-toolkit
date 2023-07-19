from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from utilies import create_next_avail_network_container
import os

app = FastAPI(description="Simple middleware to add logic for some Infoblox function")

network_map = {
    "azc_use1": {
        22: "10.99.32.0/20",
        23: "10.99.32.0/20",
        24: "10.99.48.0/20",
        25: "10.99.64.0/20",
        26: "10.99.80.0/20",
        27: "10.99.96.0/20",
        28: "10.99.96.0/20",
    },
    "azc_usc1": {
        22: "10.99.32.0/20",
        23: "10.99.32.0/20",
        24: "10.99.48.0/20",
        25: "10.99.64.0/20",
        26: "10.99.80.0/20",
        27: "10.99.96.0/20",
        28: "10.99.96.0/20",
    }
}


class DatacenterValues(str, Enum):
    azc_use1 = "azc_use1"
    azc_usc1 = "azc_usc1"


class EnvironmentValues(str, Enum):
    dv = "dv"
    qa = "qa"
    pr = "pr"


class CreateNetwork(BaseModel):
    application_name: str
    application_environment: EnvironmentValues
    cidr_size: int = Field(..., ge=22, le=28)
    datacenter: DatacenterValues

class ResponseModel(BaseModel):
    status: bool
    message: str | None = None

@app.get("/")
async def root():
    return {"message": "Got to /docs to see api documentation", 'infoblox_gm': os.getenv('INFOBLOX_GRIDMASTER')}



@app.post("/network", response_model=ResponseModel)
async def create_new_network(network: CreateNetwork):
    container_network = network_map[network.datacenter][network.cidr_size]
    new_container = create_next_avail_network_container(parent_network=container_network,
                                                        new_network_size=24,
                                                        new_network_name=f'{str(network.application_environment.value).upper()} - {str(network.application_name).upper()}')

    # return {"message": f"Hello", 'network': network, 'container_network': container_network}
    if not new_container['status']:
        raise HTTPException(status_code=400, detail=new_container['message'])
    return new_container
