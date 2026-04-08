FROM python:3.10-slim
 
WORKDIR /app
 
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
 
COPY dataset.json  ./
COPY env.py        ./
COPY agent.py      ./
COPY inference.py  ./
COPY app.py        ./
COPY openenv.yaml  ./
 
EXPOSE 7860
 
ENV PORT=7860
 
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
