import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from date import date
from keep_alive import keep_alive
from replit import db

import requests
from bs4 import BeautifulSoup
import regex as re


load_dotenv()

prefix = '$'
client = commands.Bot(command_prefix = prefix, case_insensitive = True)
"""
helper method for findClass command
"""
def getClass(className):
  page = requests.get('https://www.deanza.edu/schedule/online-classes.html')
  soup = BeautifulSoup(page.content, "html.parser")
  data = soup.find('div', class_ = 'col-xs-12 l-content')
  classes = data.select('a')
  listOfInformation = []
  for ele in classes:
      if ele.text not in listOfInformation:
          listOfInformation.append(ele.text)
  classList = [ x for x in listOfInformation if className in x]
  db['classList'] = ', '.join(classList)

"""
helper method for findProfessor method
"""
def getProfessor(teacherName):
  teacherName = teacherName
  url = "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&" \
                  "queryBy=teacherName&schoolName=De+Anza+College&schoolID=%s&query=" % 1967 + teacherName
  page = requests.get(url=url)
  soup = BeautifulSoup(page.content, "html.parser")
  website = soup.find('li', class_ = 'listing PROFESSOR')
  info = website.select('a')
  teacherWebsite = ''

  for x in info:
      if re.findall('ShowRatings', x['href']):
          teacherWebsite = 'http://ratemyprofessors.com' + x['href']

  page = requests.get(url = teacherWebsite)
  soup = BeautifulSoup(page.content, "html.parser")
  data = soup.find('div', class_ = 'RatingValue__AvgRatingWrapper-qw8sqy-3 bIUJtl')
  teacherRating = data.text
  data = soup.find_all('div', class_ = 'FeedbackItem__FeedbackNumber-uof32n-1 kkESWs')
  wouldTakeAgain = data[0].text
  levelOfDifficulty = data[1].text
  data = soup.find('div', class_ = 'Comments__StyledComments-dzzyvm-0 gRjWel')
  topRatedComment = data.text
  db['getProfessor'] = '%s has a %s on Rate My Professor.\nThe Would Take Again Rate is %s.\nThe Level of Difficulty for the Professor is %s.\nThe Top Comment for the Professor is:\n%s' %(teacherName,teacherRating, wouldTakeAgain,levelOfDifficulty,topRatedComment)

def update_homework(homeworkName, homeworkDate, dueTime):
    db["homework"] = [homeworkName, homeworkDate, dueTime]
  
@client.event
async def on_ready():
    print("We have logged in as {0.user}" .format(client))



listOfCommands = ['homework', 'deleteHomework', 'findClass', 'findProfessor', 'calculate']

@client.command(name = listOfCommands[0])
async def _homework(ctx):
  def check(msg):
    return msg.author == ctx.author and msg.channel == ctx.channel

  await ctx.send("Hello! What is the name of the homework? Type in the name of the homework assignment.")
  homeworkName = await client.wait_for('message', check = check)

  await ctx.send("What is the date of the homework assignment? Type in Month Day Year")

  homeworkDate = await client.wait_for('message', check = check)

  await ctx.send("What is the time of the homework due date? If the homework was due at midnight, type in 2400 ")

  dueTime = await client.wait_for('message', check = check)

  update_homework(homeworkName.content, homeworkDate.content, dueTime.content)

  await ctx.send("Name: %s Date: %s Time: %s" %(db['homework'][0], db['homework'][1], db['homework'][2]))
  await ctx.send("OK! I will ping everyone when %s is due!" %(db['homework'][0]))

@client.command(name = listOfCommands[1])
async def _deleteHomework(ctx):
  def check(msg):
    return msg.author == ctx.author and msg.channel == ctx.channel
  await ctx.send("What homework would you like to delete: " + db.keys())


@client.command(name = listOfCommands[2])
async def _findClass(ctx):
  def check(msg):
    return msg.author == ctx.author and msg.channel == ctx.channel
  await ctx.send('What class would you like to search for?')

  searched = await client.wait_for('message', check = check)
  await ctx.send('Got it! Loading...')
  getClass(searched.content)
  await ctx.send("De Anza Offers these Classes: " + db['classList'])
@client.command(name = listOfCommands[3])
async def _findProfessor(ctx):
  def check(msg):
    return msg.author == ctx.author and msg.channel == ctx.channel
  await ctx.send('What is the name of the professor you would like to search for?')

  teacherName = await client.wait_for('message', check = check)
  await ctx.send('Got it! Loading...')
  try:
    getProfessor(teacherName.content)
    await ctx.send(db['getProfessor'])
  except:
    await ctx.send("Oops! That professor doesn't exist")

@client.command(name = listOfCommands[4])
async def _calculate(ctx):
  def check(msg):
    return msg.author == ctx.author and msg.channel == ctx.channel
  await ctx.send('Please enter the expression you would like to calculate:')
  expression = await client.wait_for('message', check = check)
  try:
    await ctx.send('The answer is: %0.2f' %(eval(expression.content)))
  except:
    await ctx.send("Oops! Either that is not a real expression or this bot cannot evaluate that expression")
"""
for time function, allows the function to output at certain time during the day
"""
#https://stackoverflow.com/questions/15088037/python-script-to-do-something-at-the-same-time-every-day


keep_alive()
client.run("ODQxMTQxNTAxNjY0MDM0ODc2.YJicEQ.i9RLx0LPKt0FFIQsijXcBM9ut74") #calls os.getenv so the token is called privately