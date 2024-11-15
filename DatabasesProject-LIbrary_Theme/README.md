# DatabasesProject

How to start da:

1. You create an environment and install dependencies with venv, pip:
    python -m venv env
    .\env\Scripts\activate (cmd) or .\env\Scripts\Activate.ps1 (powershell)
    pip install -r requirements.txt
    
    [[[ if you want to deactivate it later type: deactivate ]]]

2. Setup the database server
    1. Open xampp control panel and start apache and mysql
	2. Go to \xampp\mysql\bin
	3. Type: 
    .\mysql -u root -p -h localhost -P 3306
	4. Password nothing (press enter)
	5. **OPTIONAL: To see version type: SELECT @@version; (current:  10.4.27-MariaDB)
	6. Insert the database schema:  source C:/{your_path}/schema.sql   (maybe it's better with forward slashes)
	7. Insert the database data: source C:/{your_path}/insert.sql
       ** IMPORTANT: if the path for sourcing contains greek characters, it won't be able to source the file **
    
3. Start the app 
    Open new terminal
    python app.py


4. go to your browser to use it:
    localhost:3000/