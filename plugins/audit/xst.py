'''
xst.py

Copyright 2007 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

import core.controllers.outputManager as om

# options
from core.data.options.option import option
from core.data.options.optionList import optionList

from core.controllers.basePlugin.baseAuditPlugin import baseAuditPlugin
from core.data.fuzzer.mutant import mutant
import core.data.parsers.urlParser as urlParser

import core.data.kb.vuln as vuln
import core.data.kb.knowledgeBase as kb
import core.data.constants.severity as severity

import re


class xst(baseAuditPlugin):
    '''
    Find Cross Site Tracing vulnerabilities. 

    @author: Josh Summitt (ascetik@gmail.com)
    '''

    def __init__(self):
        baseAuditPlugin.__init__(self)
        
        # Internal variables
        self._exec = True

    def audit(self, freq ):
        '''
        Verify xst vulns by sending a TRACE request and analyzing the response.
        '''
    
        if not self._exec:
            # Do nothing
            pass
        else:
            # Only run once
            self._exec = False  
            
            # Create a mutant based on a fuzzable request
            # It is really important to use A COPY of the fuzzable request, and not the original.
            # The reason: I'm changing the method and the URL !
            fr_copy = freq.copy()
            fr_copy.setURL( urlParser.getDomainPath( fr_copy.getURL() ) )
            fr_copy.setMethod('TRACE')
            # Add a header. I search for this value to determine if XST is valid
            original_headers = freq.getHeaders()
            original_headers['FalseHeader'] = 'XST'
            my_mutant = mutant(fr_copy)
            
            # send the request to the server and recode the response
            response = self._sendMutant( my_mutant, analyze=False )
            
            # create a regex to test the response. 
            regex = re.compile("[FalseHeader: XST]")
            if re.match(regex, response.getBody()):
                # If vulnerable record it. This will now become visible on the KB Browser
                v = vuln.vuln( freq )
                v.setPluginName(self.getName())
                v.setId( response.id )
                v.setSeverity(severity.LOW)
                v.setName( 'Cross site tracing vulnerability' )
                msg = 'The web server at "'+ response.getURL() +'" is vulnerable to'
                msg += ' Cross Site Tracing.'
                v.setDesc( msg )
                om.out.vulnerability( v.getDesc(), severity=v.getSeverity() )
                kb.kb.append( self, 'xst', v )
            
    def getPluginDeps( self ):
        '''
        @return: A list with the names of the plugins that should be runned before the
        current one.
        '''
        return []           
            
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin finds the Cross Site Tracing (XST) vulnerability.
        
        No Configurable Paramaters.
            
        The TRACE method echos back requests sent to it. This plugin sends a 
        TRACE request to the server and if the request is echoed back then XST 
        is confirmed.
        '''

    def getOptions( self ):
        '''
        @return: A list of option objects for this plugin.
        '''    
        ol = optionList()
        return ol

    def setOptions( self, OptionList ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of getOptions().
        
        @parameter OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        pass
    
    