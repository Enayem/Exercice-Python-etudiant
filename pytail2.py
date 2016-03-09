#! /usr/bin/env python
# -*- coding: latin-1 -*-

#######################################################################

"""
NAME
    pytail - cat/tail/more en python

SYNOPSIS
    pytail filename

PARAMETERS
    filename
        Nom du fichier a visualiser

OPTIONS
    --help
        This help
    --version
        Version of pytail
    --follow
        Mode 'tail -f'

DESCRIPTION
    Lance juste avec un nom de fichier, pytail affiche le fichier 
    et il est possible de le parcourir avec les touches flechees 
    ainsi que de faire des recherches dans le fichier.
    
    Lance avec l'option '-f' et un nom de fichier, pytail affiche
    la fin du fichier ainsi que les nouvelles lignes du fichier
    au fur et a mesure qu'elles sont ajoutees.

INTERACTION
    h, F1 : Affiche cette aide
    q     : Quitte l'application
    f     : Passe du mode normal au mode follow
    /     : Demarre la saisie d'une recherche vers l'avant
    ?     : Demarre la saisie d'une recherche vers l'arriere
    v     : Edite le fichier avec vim a partir de la ligne courante
    F5    : Fait flasher l'affichage
    w     : Active la molette de la souris pour se deplacer dans le fichier
    
    Mode normal :
    
    e     : Ouvre a nouveau le fichier
    s     : Sauve le fichier dans sa version affichee
    n     : Cherche la prochaine occurance de la recherche
    N     : Cherche la prochaine occurance de la recherche dans le sens inverse
    Escape: Annule la recherche
    [1-9]*: Saisie d'un numero de ligne (non implemente)
    G     : Va a ligne saisie (non implemente) ou a la derniere ligne sinon
    Home/End    : Va a la premire/derniere ligne
    Up/Down     : Va une ligne vers le bas/haut
    P.Down/P.Up : Va une page vers le bas/haut
    
    Mode follow :
        
    g     : Seules les lignes correspondant a la recherche sont affichees (grep)
    Escape: Annule la recherche et annule grep
            
    Pendant la saisie d'une recherche ou du nom d'une sauvegarde :
        
    Taper la chaine a chercher puis,
    Escape    : Annule la saisie
    Enter     : Demarre la recherche ou la sauvegarde
    Backspace : Efface le dernier caractere de la chaine saisie
    Delete    : Efface toute la chaine saisie

AUTHOR
    Written by Leonard Billich
    
BUGS
    Email bug reports to <leonard.billich@ineo.com>.
"""

#######################################################################

name = "pytail"
version = 1.0

#######################################################################

import re
import os, sys, stat
import tty, fcntl
import time
import curses, curses.ascii

#######################################################################

class pytail:
    timeoutnormal = 1000
    timeoutfollow = 50
    
    # Constructeur
    def __init__(self, filename, follow):
        self.scrollv = 0
        self.firsttime = True
        self.message = ''
        
        if follow == True:
            self.filemode = 'follow'
            self.timeout = self.timeoutfollow
        else:
            self.filemode = 'normal'
            self.timeout = self.timeoutnormal
        self.file = None
        self.filename = filename
        self.filepos = 0
        self.filereload = True
        self.filechange = False
        self.filetime = None
        self.idlesince = None
    
        self.helpmode = False
        self.helppos = 0
        
        self.searchediting = False
        self.searchstring = ''
        self.searchpos = -1
        self.searchforward = True
        self.searchrestart = False
        self.grep = False
        
        self.saving = False
        self.savename = ''
        
        self.wheelon = False
        
        #self.save_attr = tty.tcgetattr(sys.stdout)

#######################################################################
    
    def loadfile(self):
        
        if self.filetime != None:
            newfiletime = os.stat(self.filename)[stat.ST_MTIME]
            if newfiletime > self.filetime:
                self.filechange = True
        
        if self.filereload == True:
            self.filereload = False
            self.filechange = False
            
            if self.file != None:
                self.file.close()
            
            file = open(self.filename,'r')
            self.filelines = file.readlines()
            self.filetime = os.stat(self.filename)[stat.ST_MTIME]
            #self.filesize = os.stat(self.filename)[stat.ST_SIZE]
            file.close()
            self.filenblines = len(self.filelines)
            #map(lambda line: line.replace('\n',''), self.filelines)

    def refreshfile(self):
        
        if self.filereload == True:
            self.filereload = False
            if self.file != None:
                self.file.close()
                self.file = None
        
        if self.file == None:
            self.file = open(self.filename,'r')
            #filelines = self.file.readlines()
            filelines = self.readnewlines()
            self.filenblines = len(filelines)
            if self.filenblines > self.wfilelines:
                self.filepos = self.filenblines - self.wfilelines
            else:
                self.filepos = 0
            self.filelines = filelines[-self.wfilelines:]
            self.filesize = os.stat(self.filename)[stat.ST_SIZE]
            self.idlesince = time.time()
        else:
            filesize = os.stat(self.filename)[stat.ST_SIZE]
            
            if filesize < self.filesize:
                self.file.close()
                self.file = open(self.filename,'r')
                #filenewlines = self.file.readlines()
                filenewlines = self.readnewlines()
                filenewnblines = len(filenewlines)
                nbdieses = self.cols/2 - 11
                self.filelines.append('#'*nbdieses+' TRUNCATED '+'#'*nbdieses)
                self.filelines.extend(filenewlines)
                self.filenblines = filenewnblines
                self.filelines = self.filelines[-self.wfilelines:]
                if filenewnblines > self.wfilelines:
                    self.filepos = 0
                else:
                    self.filepos = filenewnblines - self.wfilelines
                self.idlesince = time.time()
            else:
                #filenewlines = self.file.readlines()
                filenewlines = self.readnewlines()
                filenewnblines = len(filenewlines)
                self.filelines.extend(filenewlines)
                self.filenblines += filenewnblines
                if self.filenblines > self.wfilelines:
                    self.filepos += filenewnblines
                self.filelines = self.filelines[-self.wfilelines:]
                if filenewnblines != 0:
                    self.idlesince = time.time()
            
            self.filesize = filesize

    def readnewlines(self):
        filenewlines = self.file.readlines()
        if self.grep == True and self.searchstring:
            try:
                regexp = re.compile(self.searchstring,re.IGNORECASE)
            except re.error:
                regexp = re.compile('.*')
            #filenewlines = filter(lambda line: line.find(self.searchstring) != -1, filenewlines)
            filenewlines = filter(lambda line: regexp.search(line) != None, filenewlines)
        return filenewlines

    def save(self):
        file = open(self.savename,"w")
        for line in self.filelines:
            file.write(line)
        file.close()
        self.message = "Current file saved as '"+self.savename+"'"

#######################################################################

    def searchnext(self, invert):
        
        if self.searchstring != '':
            self.message = ''
            
            if invert == False:
                forward = self.searchforward
            else:
                forward = not self.searchforward
                
            if self.searchrestart == True:
                self.searchrestart = False
                if forward == True:
                    self.filepos = 0
                else:
                    if self.filenblines > self.wfilelines:
                        self.filepos = self.filenblines - self.wfilelines
                    else:
                        self.filepos = 0
            
            if self.searchpos == -1:
                if forward == True:
                    searchpos = self.filepos
                else:
                    if self.filepos + self.wfilelines < self.filenblines:
                        searchpos = self.filepos + self.wfilelines - 1
                    else:
                        searchpos = self.filenblines - 1
            else:
                if forward == True:
                    searchpos = self.searchpos + 1
                else:
                    searchpos = self.searchpos - 1
                
            if forward == True:
                srange = range(searchpos, self.filenblines)
            else:
                srange = range(searchpos, -1, -1)
                
            matchfound = False
            
            try:
                regexp = re.compile(self.searchstring,re.IGNORECASE)
            except re.error:
                regexp = re.compile('.*')
            
            for pos in srange:
                
                #if self.filelines[pos].find(self.searchstring) != -1:
                if regexp.search(self.filelines[pos]) != None:
                    
                    if forward == True and pos >= self.filepos + self.wfilelines:
                        self.filepos += pos - (self.wfilelines + self.filepos) + 1
                    if forward == False and pos < self.filepos:
                        self.filepos = pos
                    
                    self.scrollv = self.filepos
                    self.searchpos = pos
                    matchfound = True
                    break

            if matchfound == False:
                if self.searchpos == -1:
                    self.message = "no match found for '" + self.searchstring + "'"
                else:
                    self.message = "no more match found for '" + self.searchstring + "'"
                    self.searchpos = -1
                    self.searchrestart = True

#######################################################################
    
    # Demarrage :
    # - Initialise curse
    # - Lance la boucle
    # - Quitte la boucle et desinitialise curse sur exception
    def start(self):
        
        try:
            self.initcurse()
            self.loadfile()
            self.updatewheader()
            self.updatewfile()
            self.updatewfooter()
            self.updatewcmd()
            self.loop()
        finally:
            self.uninitcurse()
            #import tty  #required this import here
            #tty.tcsetattr(sys.stdout, tty.TCSADRAIN, self.save_attr)

#######################################################################

    # Boucle principale
    def loop(self):
        car = -1
        #self.w.erase()

        while 1:

            self.listenkb()
            self.clearw()
            
            if self.helpmode == True:
                
                self.updatewheader()
                self.updatehelp()
                self.updatewfooter()
                
            else: # filemode
                
                if self.filemode == 'follow':
                    self.refreshfile()
                else:
                    self.loadfile()
            
                self.updatewheader()
                self.updatewfile()
                self.updatewfooter()
                self.updatewcmd()

#######################################################################

    def updatewheader(self):
        
        self.wheader.erase()
        
        if self.helpmode == True:
            filename = 'help'
            filenblines = len(__doc__.splitlines())
        else:
            filename = self.filename
            filenblines = self.filenblines

        heure = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        headerleft  = '[File: '+filename+' ('+str(filenblines)+' lines) '
        headerright = ' ' + heure + ']'
        
        nbtirets = self.cols - len(headerleft) - len(headerright)
        
        self.gotoheader()
        self.printheader( headerleft + '-'*nbtirets + headerright )
        
        self.wheader.refresh()

#----------------------------------------------------------------------

    def updatewfooter(self):
        
        self.wfooter.erase()
        
        if self.helpmode == True:
            mode = 'help'
            percent = self.progression*100/(len(__doc__.splitlines())+1)
        else:
            mode = self.filemode
            if self.filemode == 'normal':
                percent = self.progression*100/self.filenblines
            else:
                percent = 0
        
        footerleft  = '[Mode: ' + mode + ' '
        footerwarning = ''
        footerright = ']'
        
        
        if self.filemode == 'normal':
            if self.filechange == True:
                footerwarning = "(file has been modified, type 'e' to reopen) "
        elif self.idlesince != None:
            now = time.time()
            t = now - self.idlesince
            if t >= 1:
                idletime = 'idle since %02d:%02d:%02d and %d days' % ((t%(24*60*60))/(60*60), (t%(60*60))/60, t%60, (t%(24*60*60*60))/(24*60*60))
                footerwarning = '(' + idletime + ') '

        nbcolsfree = self.cols - len(footerleft) - len(footerright) - len(footerwarning)
        n1 = nbcolsfree*percent/100
        n2 = nbcolsfree-n1
        
        self.gotofooter()
        self.printfooter( footerleft )
        self.printfootercolor( footerwarning, 'red', None )
        self.printfooter( '='*n1 + '-'*n2 + footerright )
        
        self.wfooter.refresh()

#----------------------------------------------------------------------

    # Mise a jour de la fenetre de commande
    def updatewcmd(self):
        
        self.wcmd.erase()
        
        #attr = curses.A_NORMAL
        color = None
        attr = 'bold'
        
        if self.saving == True:
            command = 'SAVE AS: ' + self.savename
            color = 'red'
            attr = 'bold'
        elif self.grep == True:
            command = 'GREP: ' + self.searchstring
        elif self.searchediting == True:
            if self.searchforward == True:
                command = '/'
            else:
                command = '?'
            command += self.searchstring
        else:
            command = self.message
        
        self.gotocmd()
        self.printcmdcolor(command,color,attr)
        
        if self.cursescolors == True:
            self.w.move(self.lines-1, len(command))
        
        self.wcmd.refresh()

#----------------------------------------------------------------------

    # Mise a jour de la fenetre du fichier
    def updatewfile(self):
        
        self.wfile.erase()
        
        firstline = self.scrollv
        lastline  = self.scrollv + self.wfilelines
        
        if self.filemode == 'normal':
            filenblines = self.filenblines
        else:
            filenblines = len(self.filelines)
            
        if lastline > filenblines:
            lastline = filenblines
            
        self.progression = lastline
        
        for numline in range( firstline , lastline ):
            #self.printfileyxcolor( numline-firstline , 0 , str(numline+1).rjust(4) + '  ', self.colorgreen )
            line = self.filelines[numline].replace('\n','')
            
            self.printfileyxcolor( numline-firstline , 0 , str(numline-firstline+self.filepos+1).rjust(4) + '  ', 'green', None )
            if self.searchstring == '':
                self.printfile( line )
            else:
                if self.searchpos == numline:
                    attr1 = (None, 'standout')
                    attr2 = ('yellow', 'standout')
                else:
                    attr1 = (None, None)
                    attr2 = ('yellow', 'bold')
                
                try:
                    linesplit1 = re.compile(self.searchstring,re.IGNORECASE).split(line)
                    linesplit2 = re.compile(self.searchstring,re.IGNORECASE).findall(line)
                    linesplit2 = filter(lambda element: element != '', linesplit2)
                except re.error:
                    linesplit1 = [line]
                
                idx2 = 0
                nbsplit = len(linesplit1)
                for idx in range(nbsplit):
                    if idx > 0 and idx < nbsplit:
                        #self.printfilecolor( self.searchstring, attr2 )
                        self.printfilecolor( linesplit2[idx2], attr2[0], attr2[1] )
                        idx2 += 1
                    if linesplit1[idx]:
                        self.printfilecolor( linesplit1[idx], attr1[0], attr1[1] )
        
        self.wfile.refresh()

#----------------------------------------------------------------------

    # Mise a jour de la fenetre d'aide
    def updatehelp(self):
        
        #self.wcmd.erase()
        #self.printcmd('Help: Type <F1> again to quit help')
        #self.wcmd.border()
        #self.wcmd.refresh()
        
        self.wfile.erase()
        
        lines = []
        lines.append(name+' '+str(version))
        lines.extend(__doc__.splitlines())
        nblines = len(lines)
        
        firstline = self.scrollv
        lastline  = self.scrollv + self.wfilelines
        if lastline > nblines:
            lastline = nblines
        
        self.progression = lastline
        
        for numline in range( firstline , lastline ):
            if lines[numline].isupper() == False:
                self.printfileyx( numline-firstline , 0 , lines[numline] )
            else:
                self.printfileyxcolor( numline-firstline , 0 , lines[numline], None, 'bold' )
            
        self.wfile.refresh()

#######################################################################

    # Actions clavier
    # - Lit une touche (attend updatedelay ou une touche puis continu)
    def listenkb(self):
        if self.firsttime == True:
            self.firsttime = False
            self.w.timeout(0)
            car = self.w.getch()
            self.w.timeout(self.timeout)
        else:
            car = self.w.getch()
            
        if car != -1:
            if car == curses.KEY_F5:
                curses.flash()
            if curses.ascii.isgraph(car) and curses.ascii.unctrl(car) in ['q', 'Q']:
                sys.exit(0)
            if curses.ascii.isgraph(car) and curses.ascii.unctrl(car) in ['w', 'W']:
                self.wheelon = not self.wheelon
                self.initwheel()
            if self.saving == True:
                self.listenkbsavemode(car)
            elif self.searchediting == True:
                self.listenkbsearcheditmode(car)
            elif self.helpmode == True:
                self.listenkbhelpmode(car)
            else:
                self.listenkbfilemode(car)

    # Actions clavier (mode normal et follow)
    def listenkbfilemode(self,car):
        if car == curses.ascii.ESC:
            if self.searchstring != '':
                self.searchstring = ''
                if self.grep == True:
                    self.filereload = True
                    self.grep = False
        elif car == curses.KEY_F1:
            self.scrollv = self.helppos
            self.helpmode = True
            curses.curs_set(0)
        elif curses.ascii.isgraph(car) and curses.ascii.unctrl(car) in ['v', 'V']:
            curses.endwin()
            os.system('vim ' + self.filename + " +" + str(self.filepos+1))
            self.w = curses.initscr()
            curses.curs_set(0)
        elif curses.ascii.isgraph(car) and curses.ascii.unctrl(car) == '/':
            self.searchforward = True
            self.searchediting = True
            #self.searchstring = ''
            self.searchpos = -1
            self.message = ''
            if self.grep == True:
                self.grep = False
                self.filereload = True
        elif curses.ascii.isgraph(car) and curses.ascii.unctrl(car) == '?':
            self.searchforward = False
            self.searchediting = True
            #self.searchstring = ''
            self.searchpos = -1
            self.message = ''
            if self.grep == True:
                self.grep = False
                self.filereload = True
        elif self.filemode == 'normal':
            self.listenkbnormalmode(car)
        else:
            self.listenkbfollowmode(car)

    # Actions clavier (mode normal)
    def listenkbnormalmode(self,car):
        if curses.ascii.isgraph(car) and curses.ascii.unctrl(car) in ['f', 'F']:
            self.filemode = 'follow'
            self.timeout = 50
            self.w.timeout(self.timeout)
            self.file = None
            self.scrollv = 0
            self.searchpos = -1
        elif curses.ascii.isgraph(car) and curses.ascii.unctrl(car) in ['e', 'E']:
            self.filereload = True
        elif curses.ascii.isgraph(car) and curses.ascii.unctrl(car) == 'n':
            self.searchnext(False)
        elif curses.ascii.isgraph(car) and curses.ascii.unctrl(car) == 'N':
            self.searchnext(True)
        elif curses.ascii.isgraph(car) and curses.ascii.unctrl(car) in ['s', 'S']:
            dateheure = time.strftime('_%Y-%m-%d_%H-%M-%S', time.localtime())
            self.savename = self.filename + dateheure
            self.saving = True
        else:
            self.listenkbscroll(car)

    # Actions clavier (mode follow)
    def listenkbfollowmode(self,car):
        if curses.ascii.isgraph(car) and curses.ascii.unctrl(car) in ['f', 'F']:
            self.filemode = 'normal'
            self.timeout = 1000
            self.w.timeout(self.timeout)
            self.scrollv = self.filepos
            self.filereload = True
            self.grep = False
        if curses.ascii.isgraph(car) and curses.ascii.unctrl(car) == 'g':
            if self.searchstring != '':
                self.filereload = True
                self.grep = not self.grep

    # Actions clavier (mode searchedit)
    def listenkbsavemode(self,car):
        if car == curses.ascii.ESC:
            self.saving = False
            self.savename = ''
        elif car == 13: #(touche enter)
            if self.savename != '':
                self.saving = False
                self.save()
        elif car == curses.KEY_BACKSPACE:
            self.savename = self.savename[:-1]
        elif car == curses.KEY_DC:
            self.savename = ''
        elif curses.ascii.isprint(car):
            self.savename += curses.ascii.unctrl(car)

    # Actions clavier (mode searchedit)
    def listenkbsearcheditmode(self,car):
        if car == curses.ascii.ESC:
            self.searchediting = False
            self.searchstring = ''
        elif car == 13: #(touche enter)
            self.searchediting = False
            if self.filemode == 'normal':
                self.searchnext(False)
        elif car == curses.KEY_BACKSPACE:
            self.searchstring = self.searchstring[:-1]
        elif car == curses.KEY_DC:
            self.searchstring = ''
        elif curses.ascii.isprint(car):
            self.searchstring += curses.ascii.unctrl(car)

    # Actions clavier (mode aide)
    # - <F1> Quitte l'aide
    # - Touches de defilement, parcours l'aide
    def listenkbhelpmode(self,car):
        if car == curses.KEY_F1:
            self.scrollv = self.filepos
            self.helpmode = False
            curses.curs_set(1)
        else:
            self.listenkbscroll(car)

    # Actions clavier (defilement du fichier)
    # - <UP> / <DOWN> Defile d'une ligne
    # - <PAGE-UP> / <PAGE-DOWN> Defile d'une page
    # - <HOME> / <END> Defile de tout le fichier
    def listenkbscroll(self,car):
        if car == curses.KEY_DOWN or car == 13:
            self.scroll(1)
        elif car == curses.KEY_UP:
            self.scroll(-1)
        elif car == curses.KEY_NPAGE or car == curses.ascii.SP:
            self.scroll(self.wfilelines-1)
        elif car == curses.KEY_PPAGE:
            self.scroll(-(self.wfilelines-1))
        elif car == curses.KEY_HOME:
            if self.helpmode == True:
                nblines = len(__doc__.splitlines())+1
            else:
                nblines = self.filenblines
            self.scroll(-nblines)
        elif car == curses.KEY_END or (curses.ascii.isgraph(car) and curses.ascii.unctrl(car) == 'G'):
            if self.helpmode == True:
                nblines = len(__doc__.splitlines())+1
            else:
                nblines = self.filenblines
            self.scroll(nblines)
        elif car == curses.KEY_MOUSE:
            mouse = curses.getmouse()
            if mouse[4] in [134217728, 128]:
                self.scroll(2)
            elif mouse[4] == 524288:
                self.scroll(-2)
            elif mouse[4] == 2:
                mousex = mouse[1]
                if mousex < 15:
                    percent = 0
                elif mousex > self.cols-1:
                    percent = 100
                else:
                    percent = (mousex-15) * 100 / (self.cols-17)
                if self.filenblines > self.wfilelines:
                    nblines = self.filenblines - self.wfilelines
                    self.scrollv = nblines * percent / 100
                    if self.helpmode == True:
                        self.helppos = self.scrollv
                    else:
                        self.filepos = self.scrollv

    # Defile d'un nombre de lignes dans le fichier
    def scroll(self,value):
        self.scrollv = self.scrollv + value

        if self.helpmode == True:
            min = 0
            max = len(__doc__.splitlines())+1-self.wfilelines
        else:
            min = 0
            if self.filenblines > self.wfilelines:
                max = self.filenblines-self.wfilelines
            else:
                max = 0

        if self.scrollv < min:
            self.scrollv = min
        elif self.scrollv > max:
            self.scrollv = max

        if self.helpmode == True:
            self.helppos = self.scrollv
        else:
            self.filepos = self.scrollv

#######################################################################

    # Initialisation de curse
    def initcurse(self):
        
        # Check the terminal type.  If we fail, then assume that the
        # terminal has no capabilities.
        try: curses.setupterm()
        except: return
        
        #self.colors = cursescolors()
        
        self.cols = curses.tigetnum('cols')
        self.lines = curses.tigetnum('lines')
        self.wfilelines = self.lines-3

        self.w = curses.initscr()
        # fenetre                    hauteur          largeur    y             x
        self.wheader = curses.newwin(              1, self.cols,            0, 0)
        self.wfile   = curses.newwin(self.wfilelines, self.cols,            1, 0)
        self.wfooter = curses.newwin(              1, self.cols, self.lines-2, 0)
        self.wcmd    = curses.newwin(              1, self.cols, self.lines-1, 0)
        curses.noecho()
        curses.cbreak()
        curses.nonl() # permet d'activer la touche enter (code 13)
        curses.curs_set(0)
        curses.mousemask(0)
        curses.mouseinterval(0)
        self.w.keypad(1)
        self.w.nodelay(0)
        self.w.timeout(self.timeout)
        
        try:
            self.initcolors_1()
        except:
            self.initcolors_2()
        
    def initcolors_1(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, -1, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        curses.init_pair(5, curses.COLOR_BLUE, -1)
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        
        color = {}
        color['normal'] = curses.color_pair(1)
        color['green']  = curses.color_pair(2)
        color['red']    = curses.color_pair(3)
        color['yellow'] = curses.color_pair(4)
        color['blue']   = curses.color_pair(5)
        color['cyan']   = curses.color_pair(6)
        self.color = color
        
        attribute = {}
        attribute['normal']   = curses.A_NORMAL
        attribute['standout'] = curses.A_STANDOUT
        attribute['bold']     = curses.A_BOLD
        self.attribute = attribute
        
        self.cursescolors = True
        
    def initcolors_2(self):
        def getcolor(c):
            return curses.tparm(curses.tigetstr("setf"), c)
        color = {}
        color['blue']   = getcolor(1)
        color['green']  = getcolor(2)
        color['cyan']   = getcolor(3)
        color['red']    = getcolor(4)
        color['yellow'] = getcolor(6)
        color['normal'] = getcolor(9)
        self.color = color
        
        def getattribute(a):
            return curses.tparm(curses.tigetstr(a))
        attribute = {}
        attribute['normal']   = getattribute('sgr0')
        attribute['standout'] = getattribute('smso')
        attribute['bold']     = getattribute('bold')
        self.attribute = attribute
        
        self.cursescolors = False
        
    def initwheel(self):
        if self.wheelon == False:
            curses.mousemask(0)
        else:
            curses.mousemask(curses.BUTTON1_CLICKED | curses.BUTTON2_CLICKED | curses.BUTTON3_CLICKED | curses.BUTTON4_CLICKED |
                            curses.BUTTON1_PRESSED | curses.BUTTON2_PRESSED | curses.BUTTON3_PRESSED | curses.BUTTON4_PRESSED |
                            curses.BUTTON1_RELEASED | curses.BUTTON2_RELEASED | curses.BUTTON3_RELEASED | curses.BUTTON4_RELEASED )
        
#----------------------------------------------------------------------
            
    # Desinitialisation de curse pour que le terminal reste utilisable
    def uninitcurse(self):
        
        curses.echo()
        curses.nocbreak();
        curses.curs_set(1)
        self.w.keypad(0);
        curses.endwin()
    
#######################################################################

    def gotofile(self):
        self.gotoyx((1, 0))
        
    # Affiche du texte dans la fenetre du fichier
    def printfile(self, arg):
        self.printw(self.wfile, arg)

    def printfilecolor(self, arg, color, attr):
        self.printw(self.wfile, arg, color, attr)

    # Affiche du texte dans la fenetre du fichier (aux coordonnees indiquees)
    def printfileyx(self, y, x, arg):
        if self.cursescolors == False: y += 1
        self.printwyx(self.wfile, (y, x), arg)

    def printfileyxcolor(self, y, x, arg, color, attr):
        if self.cursescolors == False: y += 1
        self.printwyx(self.wfile, (y, x), arg, color, attr)

#----------------------------------------------------------------------

    def gotocmd(self):
        self.gotoyx((self.lines-1, 0))

    # Affiche du texte dans la fenetre de commandes
    def printcmd(self, arg):
        self.printw(self.wcmd, arg)

    def printcmdcolor(self, arg, color, attr):
        self.printw(self.wcmd, arg, color, attr)

#----------------------------------------------------------------------

    def gotoheader(self):
        self.gotoyx((0, 0))

    def printheader(self, arg):
        #self.printw(self.wheader, arg, 'green', 'bold')
	self.printw(self.wheader, arg, 'green')

#----------------------------------------------------------------------

    def gotofooter(self):
        self.gotoyx((self.lines-2, 0))

    def printfooter(self, arg):
        #self.printw(self.wfooter, arg, 'green', 'bold')
	self.printw(self.wfooter, arg, 'green')

    def printfootercolor(self, arg, color, attr):
        self.printw(self.wfooter, arg, color, attr)

#----------------------------------------------------------------------

    def printw(self, window, arg, color = None, attribute = None):
        self.printwyx(window, None, arg, color, attribute)

    def printwyx(self, window, coord, arg, color = None, attribute = None):
        if self.cursescolors == True:
            try:
                if color or attribute:
                    attr = 0
                    if color: attr |= self.color[color]
                    if attribute: attr |= self.attribute[attribute]
                    if coord:
                        window.addstr(coord[0], coord[1], arg, attr)
                    else:
                        window.addstr(arg, attr)
                elif coord:
                    window.addstr(coord[0], coord[1], arg)
                else:
                    window.addstr(arg)
            except curses.error:
                pass
        else:
            coordstr = ""
            if coord: coordstr = curses.tparm(curses.tigetstr("cup"), coord[0], coord[1])
            colorstr = self.attribute['normal']
            if color: colorstr += self.color[color]
            if attribute: colorstr += self.attribute[attribute]
            clr_eol = curses.tparm(curses.tigetstr("el"))
            curses.putp(coordstr + colorstr + arg + clr_eol)

    def gotoyx(self, coord):
        if self.cursescolors == False:
            curses.putp(curses.tparm(curses.tigetstr("cup"), coord[0], coord[1]))

    def clearw(self):
        if self.cursescolors == False:
            #curses.putp(curses.tparm(curses.tigetstr("clear")))
            pass

#######################################################################

def printUsage():
    print __doc__

#----------------------------------------------------------------------

def printVersion():
    print name, version

#----------------------------------------------------------------------

def main(argv):

    import getopt

    try:
        opts, args = getopt.getopt(argv, "hvf", ["help", "version", "follow"])
    except getopt.GetoptError:
        print "Erreur : arguments invalides"
        sys.exit(2)

    follow = False
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printUsage()
            sys.exit()
        elif opt in ("-v", "--version"):
            printVersion()
            sys.exit()
        elif opt in ("-f", "--follow"):
            follow = True

    if args == []:
        print "Erreur : aucun argument"
        sys.exit(2)
    else:
        if os.path.exists(args[0]):
            if os.path.isfile(args[0]):
                pytail(args[0], follow).start()
            else:
                print "Erreur : "+args[0]+" n'est pas un fichier"
        else:
            print "Erreur : "+args[0]+" n'existe pas"
    

#######################################################################

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass

#######################################################################
