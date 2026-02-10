# 1.base image
FROM python:3.10-slim

#2.Set working directory
WORKDIR /client

#3. Copy requirements
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

#5.Copy the whole project
COPY . . 

# 6. Expose port (optional)
EXPOSE 3000

#  7. Run the app
CMD ["uvicorn", "app.main:app", "--host" ,"0.0.0.0", "--port", "3000"]