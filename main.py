from fastapi import FastAPI, Body, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from scripts import Binder_Pdf, GaragingProof
from pathlib import Path
from zipfile import ZipFile
import tempfile
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF Generator API",
    description="API para gerar PDFs de Binder e Garaging Proof",
    version="1.0.0"
)

def cleanup_file(file_path: str):
    """Remove arquivo temporário após o download"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Arquivo temporário removido: {file_path}")
    except Exception as e:
        logger.error(f"Erro ao remover arquivo temporário {file_path}: {e}")

@app.get("/")
def read_root():
    """Endpoint de status da API"""
    return {"message": "PDF Generator API está funcionando!", "status": "online"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/generate-pdf/")
def generate_pdf(
    background_tasks: BackgroundTasks,
    state: str = Body(..., description="Estado (ex: SP, RJ)"),
    city: str = Body(..., description="Cidade"),
    zip_code: str = Body(..., description="CEP"),
    full_name: str = Body(..., description="Nome completo"),
    address: str = Body(..., description="Endereço completo"),
    new_policy_start_date: str = Body(..., description="Data de início da apólice (YYYY/MM/DD)"),
    vehicle_year: str = Body(..., description="Ano do veículo"),
    vehicle_make: str = Body(..., description="Marca do veículo"),
    vehicle_model: str = Body(..., description="Modelo do veículo"),
    vehicle_vin: str = Body(..., description="VIN do veículo"),
    lienholder: bool = Body(False, description="Possui financiamento?"),
    lien_name: str = Body("", description="Nome do financiador"),
    lien_address: str = Body("", description="Endereço do financiador"),
    lien_city_state_zip: str = Body("", description="Cidade, Estado e CEP do financiador"),
    garaging_proof: bool = Body(False, description="Gerar comprovante de garagem?"),
):
    """
    Gera PDFs de Binder e opcionalmente Garaging Proof, retornando um arquivo ZIP
    """
    try:
        # Validações básicas
        if not full_name.strip():
            raise HTTPException(status_code=400, detail="Nome completo é obrigatório")
        
        if lienholder and not lien_name.strip():
            raise HTTPException(status_code=400, detail="Nome do financiador é obrigatório quando lienholder=true")

        # Preparar dados
        first_name = full_name.strip().split()[0].upper()
        city_state_zip = f"{city} {state} {zip_code}".upper()
        if not lienholder:
            lien_name = ""
            lien_address = ""
            lien_city_state_zip = ""

        logger.info(f"Iniciando geração de PDFs para: {full_name}")

        # Cria diretório temporário
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pdfs_gerados = []

            try:
                # Gera o PDF do Binder
                logger.info("Gerando PDF do Binder...")
                binder = Binder_Pdf(
                    state, full_name, address, city_state_zip, new_policy_start_date,
                    vehicle_year, vehicle_make, vehicle_model, vehicle_vin,
                    lienholder, lien_name, lien_address, lien_city_state_zip
                )
                binder.insert_info()
                binder_file = temp_path / f"binder_{first_name}.pdf"
                binder.salvar(str(binder_file))
                
                if binder_file.exists():
                    pdfs_gerados.append(binder_file)
                    logger.info(f"Binder PDF gerado: {binder_file}")
                else:
                    raise HTTPException(status_code=500, detail="Erro ao gerar PDF do Binder")

            except Exception as e:
                logger.error(f"Erro ao gerar Binder PDF: {e}")
                raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF do Binder: {str(e)}")

            if garaging_proof:
                try:
                    logger.info("Gerando PDFs de Garaging Proof...")
                    garaging = GaragingProof(
                        state, full_name, address, city_state_zip, new_policy_start_date
                    )
                    
                    garaging_file_1 = temp_path / f"{garaging.bill_1}_{first_name}.pdf"
                    garaging_file_2 = temp_path / f"{garaging.bill_2}_{first_name}.pdf"
                    
                    garaging.insert_info_to_dir(str(garaging_file_1), str(garaging_file_2))
                    
                    if garaging_file_1.exists():
                        pdfs_gerados.append(garaging_file_1)
                        logger.info(f"Garaging Proof 1 gerado: {garaging_file_1}")
                    
                    if garaging_file_2.exists():
                        pdfs_gerados.append(garaging_file_2)
                        logger.info(f"Garaging Proof 2 gerado: {garaging_file_2}")

                except Exception as e:
                    logger.error(f"Erro ao gerar Garaging Proof PDFs: {e}") # Aqui não falha completamente, só loga o erro.
                    logger.warning("Continuando sem os PDFs de Garaging Proof")

            if not pdfs_gerados:
                raise HTTPException(status_code=500, detail="Nenhum PDF foi gerado com sucesso")

            # Cria arquivo ZIP final
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip', prefix=f'{first_name}_docs_')
            temp_zip.close()

            try:
                with ZipFile(temp_zip.name, "w") as zipf:
                    for pdf in pdfs_gerados:
                        if pdf.exists():
                            zipf.write(pdf, pdf.name)
                            logger.info(f"Adicionado ao ZIP: {pdf.name}")

                logger.info(f"ZIP criado com sucesso: {temp_zip.name}")
                
                # Limpeza do arquivo
                background_tasks.add_task(cleanup_file, temp_zip.name)

                return FileResponse(
                    temp_zip.name,
                    media_type="application/zip",
                    filename=f"{first_name}_documents.zip",
                    headers={
                        "Content-Disposition": f"attachment; filename={first_name}_documents.zip"
                    }
                )

            except Exception as e:
                # Limpar o arquivo zip em caso de erro
                cleanup_file(temp_zip.name)
                logger.error(f"Erro ao criar ZIP: {e}")
                raise HTTPException(status_code=500, detail=f"Erro ao criar arquivo ZIP: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint não encontrado", "detail": "Verifique a URL e tente novamente"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Erro interno do servidor", "detail": "Tente novamente mais tarde"}


if __name__ == "__main__":
    import uvicorn
    # Render define a variável PORT automaticamente
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )