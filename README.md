# **UV tasks and mails monitor**
> **Lucas Arroyo Blanco**
> 
> **PatoOsoPatoso**  

* [monitor_virtual.py](monitor_virtual.py) is used to monitor the new tasks that appear in the aulavirtual and send a telegram notification when some new task is detected.  
* [monitor_mail.py](monitor_mail.py) is similar but instead of monitoring the new tasks, this script detects new mails and sends a telegram notification.
## Modifications to be used
To use the code as it is right now first you are going to need to create a **.env** file.  
The file should look like this
```
UV_USER=...
UV_PASS=...
TELEGRAM_TOKEN=...
CHAT_ID=...
```
In [monitor_virtual.py](monitor_virtual.py)	change `year = '2021-2022'` to your current years.  
&nbsp;  

<img src="https://static.wikia.nocookie.net/horadeaventura/images/c/c2/CaracolRJS.png/revision/latest?cb=20140518032802&path-prefix=es" alt="drawing" style="width:100px;"/>