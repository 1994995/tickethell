# DEV setup (this is janky, I'll make it better later)
Have `Python` installed
open the project with an IDE or terminal (I guess) to /backend 
run `Python3 -m venv .venv` (or name ur venv whatever u want I don't care)
run `Python3 .venv/bin/activate` to activate the Python environment
run `pip3 install -r requirements.txt` to install required packages
*after installing you might need to restart the environment to get SSL certificates to work idk*
create a `.env` file in the root directory (i.e. /backend/.env) with the following field names:
  `SMTP_HOST=smtp.gmail.com`
  `SMTP_PORT=587`
  `SMTP_USER=<your_email@gmail.com>`
  `SMTP_PASSWORD=<your gmail app password>`
  `FROM_EMAIL=<whatever email u want to send from, probably SMTP_USER`
  For setting up a gmail app password see: https://support.google.com/mail/answer/185833?hl=en
  *For now this assume gmail. In theory it could be any email provider which allows SMTP but not right now*
  **run `fastapi dev` and click on the .../docs link to see API endpoints**
  *Hopefully everything just works. If not idk how to help u right now we'll deal with that later*
