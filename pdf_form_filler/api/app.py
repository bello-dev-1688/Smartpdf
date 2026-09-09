from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pdf_form_filler.api.health import router as health_router
from pdf_form_filler.api.documents import router as documents_router
from pdf_form_filler.api.fields import router as fields_router
from pdf_form_filler.api.signatures import router as signatures_router
from pdf_form_filler.api.render import router as render_router
from pdf_form_filler.api.export import router as export_router

app=FastAPI(title='PDF Form Filler API',version='1.2.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['*'],allow_headers=['*'])
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(fields_router)
app.include_router(signatures_router)
app.include_router(render_router)
app.include_router(export_router)
