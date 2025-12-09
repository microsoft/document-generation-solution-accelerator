"""
Generate Solution Architecture Diagram for Content Generation Accelerator
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import ContainerInstances, AppServices, ContainerRegistries
from diagrams.azure.database import CosmosDb, BlobStorage
from diagrams.azure.ml import CognitiveServices, AzureOpenAI
from diagrams.azure.web import AppServices as WebApp
from diagrams.azure.network import VirtualNetworks, PrivateEndpoint
from diagrams.programming.framework import React
from diagrams.programming.language import Python
from diagrams.generic.storage import Storage
from diagrams.onprem.client import User

# Graph attributes for dark theme matching the reference image
graph_attr = {
    "bgcolor": "#1a2634",
    "fontcolor": "white",
    "fontsize": "14",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "1.5",
}

node_attr = {
    "fontcolor": "white",
    "fontsize": "11",
}

edge_attr = {
    "color": "#4a9eff",
    "style": "bold",
}

with Diagram(
    "Content Generation Solution Architecture",
    filename="/home/jahunte/content-generation-solution-accelerator/docs/images/readme/solution_architecture",
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    user = User("User")
    
    with Cluster("Azure Cloud", graph_attr={"bgcolor": "#243447", "fontcolor": "white"}):
        
        with Cluster("Frontend Tier"):
            app_service = AppServices("App Service\n(Node.js)")
            
        with Cluster("Container Registry"):
            acr = ContainerRegistries("Azure Container\nRegistry")
        
        with Cluster("Backend Tier (VNet Integrated)"):
            aci = ContainerInstances("Container Instance\n(Python/Quart)")
        
        with Cluster("AI Services"):
            aoai_gpt = CognitiveServices("Azure OpenAI\n(GPT-5.1)")
            aoai_dalle = CognitiveServices("Azure OpenAI\n(DALL-E 3)")
        
        with Cluster("Data Storage"):
            cosmos = CosmosDb("Cosmos DB\n(Briefs, Products,\nChat History)")
            blob = BlobStorage("Blob Storage\n(Product Images,\nGenerated Content)")
    
    # User flow
    user >> Edge(label="HTTPS") >> app_service
    
    # App Service to Backend
    app_service >> Edge(label="API Proxy\n(Private VNet)") >> aci
    
    # Container Registry
    acr >> Edge(label="Pull Image") >> aci
    
    # Backend to AI Services
    aci >> Edge(label="Content\nGeneration") >> aoai_gpt
    aci >> Edge(label="Image\nGeneration") >> aoai_dalle
    
    # Backend to Data
    aci >> Edge(label="CRUD\nOperations") >> cosmos
    aci >> Edge(label="Store/Retrieve\nImages") >> blob
