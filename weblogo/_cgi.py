#!/usr/bin/env python

#  Copyright (c) 2003-2004 The Regents of the University of California.
#  Copyright (c) 2005 Gavin E. Crooks
#  Copyright (c) 2006, The Regents of the University of California, through 
#  Lawrence Berkeley National Laboratory (subject to receipt of any required
#  approvals from the U.S. Dept. of Energy).  All rights reserved.

#  This software is distributed under the new BSD Open Source License.
#  <http://www.opensource.org/licenses/bsd-license.html>
#
#  Redistribution and use in source and binary forms, with or without 
#  modification, are permitted provided that the following conditions are met: 
#
#  (1) Redistributions of source code must retain the above copyright notice, 
#  this list of conditions and the following disclaimer. 
#
#  (2) Redistributions in binary form must reproduce the above copyright 
#  notice, this list of conditions and the following disclaimer in the 
#  documentation and or other materials provided with the distribution. 
#
#  (3) Neither the name of the University of California, Lawrence Berkeley 
#  National Laboratory, U.S. Dept. of Energy nor the names of its contributors 
#  may be used to endorse or promote products derived from this software 
#  without specific prior written permission. 
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
#  POSSIBILITY OF SUCH DAMAGE. 



import sys
import cgi as cgilib
import cgitb; cgitb.enable()

#print "Content-Type: text/html\n\n"
#print "HELLO WORLD"
#print __name__

from StringIO import StringIO
from weblogo.color import *
from weblogo.colorscheme import ColorScheme, ColorGroup
from weblogo._corebio.utils import *
from weblogo._corebio._future import Template

import weblogo



# TODO: Check units

# TODO: In WebLogo2: why slash create.cgi? I think this was a workaround
# for some browser quirk
#<form method="post" action="/create.cgi" enctype="multipart/form-data">
    
def resource_string(resource, basefilename) :
    import os
    fn =  os.path.join(os.path.dirname(basefilename), resource)
    return open( fn ).read()

    

mime_type = {
    'eps': 'application/postscript', 
    'pdf': 'application/pdf',
    'png': 'image/png',
    'png_print': 'image/png',    
    'txt' : 'text/plain',          # FIXME: Implement
    'jpeg'  : 'image/jpeg',
}

extension = {
    'eps': 'eps',
    'pdf': 'pdf',
    'png': 'png',
    'png_print': 'png',
    'txt' : 'txt',          # FIXME: Implement
    'jpeg'  : 'png'
}


alphabets = {
    'alphabet_auto': None, 
    'alphabet_protein': weblogo.unambiguous_protein_alphabet, 
    'alphabet_rna': weblogo.unambiguous_rna_alphabet,
    'alphabet_dna': weblogo.unambiguous_dna_alphabet}

color_schemes = {}
for k in weblogo.std_color_schemes.keys():
    color_schemes[ 'color_'+k.replace(' ', '_')] = weblogo.std_color_schemes[k]
    

composition = {'comp_none' : 'none',
    'comp_auto' : 'auto',
    'comp_equiprobable':'equiprobable',
    'comp_CG': 'CG',
    'comp_Celegans' : 'C. elegans',
    'comp_Dmelanogaster' : 'D. melanogaster',
    'comp_Ecoli' : 'E. coli',
    'comp_Hsapiens': 'H. sapiens',
    'comp_Mmusculus' : 'M. musculus',
    'comp_Scerevisiae': 'S. cerevisiae'
}

class Field(object) :
    """ A representation of an HTML form field."""
    def __init__(self, name, default=None, conversion= None, options=None, errmsg="Illegal value.") :
        self.name = name
        self.default = default
        self.value = default
        self.conversion = conversion        
        self.options = options
        self.errmsg = errmsg

    def get_value(self) :
        if self.options :
            if not self.value in self.options :
                raise ValueError, (self.name, self.errmsg)
                
        if self.conversion :
            try :
                return self.conversion(self.value)
            except ValueError, e :
                raise LogoValueError, (self.name, self.errmsg)
        else:
            return self.value
    
    
def string_or_none(value) :
    if value is None or value == 'auto':
        return None
    return str(value)
    
def truth(value) :
    if value== "true" : return True
    return bool(value)

def int_or_none(value) :
    if value =='' or value is None or value == 'auto':
        return None
    return int(value)
    
def float_or_none(value) :
    if value =='' or value is None or value == 'auto':
        return None
    return float(value)
        

def main(htdocs_directory = None) :
 
    # name, value, options, callback? 
    logooptions = weblogo.LogoOptions() 
    
    # A list of form fields.
    # The default for checkbox values must be False (irrespective of
    # the default in logooptions) since a checked checkbox returns 'true'
    # but an unchecked checkbox returns nothing.
    controls = [
        Field( 'sequences', ''),
        Field( 'format', 'png_print', weblogo.formatters.get ,
            options=['png_print', 'png', 'jpeg', 'eps', 'pdf', 'txt'] , errmsg="Unknown format option."),
        Field( 'stacks_per_line', logooptions.stacks_per_line , int, 
            errmsg='Invalid number of stacks per line.'),
        Field( 'size','medium', weblogo.std_sizes.get,
            options=['small', 'medium', 'large'], errmsg='Invalid logo size.'),
        Field( 'alphabet','alphabet_auto', alphabets.get,
            options=['alphabet_auto', 'alphabet_protein', 'alphabet_dna', 'alphabet_rna'],
            errmsg="Unknown sequence type."),
        Field( 'unit_name', 'bits', 
            options=[ 'probability', 'bits', 'nats', 'kT', 'kJ/mol', 'kcal/mol']),
        Field( 'first_index', 1, int),
        Field( 'logo_start', '', int_or_none),
        Field( 'logo_end', '', int_or_none),
        Field( 'composition', 'comp_auto', composition.get,
            options=['comp_none','comp_auto','comp_equiprobable','comp_CG',
            'comp_Celegans','comp_Dmelanogaster','comp_Ecoli',
            'comp_Hsapiens','comp_Mmusculus','comp_Scerevisiae'], 
            errmsg= "Illegal sequence composition."),
        Field( 'percentCG', '', float_or_none, errmsg="Invalid CG percentage."),
        Field( 'show_errorbars', False , truth),
        Field( 'logo_title', logooptions.logo_title ),
        Field( 'logo_label', logooptions.logo_label ),
        Field( 'show_xaxis', False, truth),
        Field( 'xaxis_label', logooptions.xaxis_label ),
        Field( 'show_yaxis', False, truth),     #TODO: CHECK
        Field( 'yaxis_label', logooptions.yaxis_label, string_or_none ),
        Field( 'yaxis_scale', logooptions.yaxis_scale , float_or_none,
            errmsg="The yaxis scale must be a positive number." ),
        Field( 'yaxis_tic_interval', logooptions.yaxis_tic_interval , float_or_none),
        Field( 'show_ends', False, truth), 
        Field( 'show_fineprint', False , truth), 
        Field( 'color_scheme', 'color_auto', color_schemes.get,
            options=color_schemes.keys() ,
            errmsg = 'Unknown color scheme'),
        Field( 'color0', ''),
        Field( 'symbols0', ''),
        Field( 'desc0', ''),
        Field( 'color1', ''),
        Field( 'symbols1', ''),
        Field( 'desc1', ''),
        Field( 'color2', ''),
        Field( 'symbols2', ''),
        Field( 'desc2', ''),
        Field( 'color3', ''),
        Field( 'symbols3', ''),
        Field( 'desc3', ''),
        Field( 'color4', ''),
        Field( 'symbols4', ''),
        Field( 'desc4', ''),
        ]
    
    form = {}
    for c in controls :
        form[c.name] = c


    form_values = cgilib.FieldStorage()
    
    # Send default form?
    if len(form_values) ==0 or form_values.has_key("cmd_reset"):
        # Load default truth values now.
        form['show_errorbars'].value = logooptions.show_errorbars
        form['show_xaxis'].value = logooptions.show_xaxis
        form['show_yaxis'].value = logooptions.show_yaxis
        form['show_ends'].value = logooptions.show_ends
        form['show_fineprint'].value = logooptions.show_fineprint
        
        send_form(controls, htdocs_directory = htdocs_directory) 
        return

    
    # Get form content
    for c in controls :
        c.value = form_values.getfirst( c.name, c.default) 
       
       
    options_from_form = ['format', 'stacks_per_line', 'size', 
        'alphabet', 'unit_name', 'first_index', 'logo_start','logo_end', 'composition', 
        'show_errorbars', 'logo_title', 'logo_label', 'show_xaxis', 'xaxis_label',
        'show_yaxis', 'yaxis_label', 'yaxis_scale', 'yaxis_tic_interval',
        'show_ends', 'show_fineprint']
    
    errors = []
    for optname in options_from_form :
        try :
            value =  form[optname].get_value()
            if value!=None : setattr(logooptions, optname, value)
        except ValueError, err :
            errors.append(err.args)            

    
    # Construct custom color scheme
    custom = ColorScheme()
    for i in range(0,5) :
        color = form["color%d"%i].get_value()
        symbols = form["symbols%d"%i].get_value()
        desc = form["desc%d"%i].get_value() 

        if color :
            try :
                custom.groups.append( weblogo.ColorGroup( symbols, color, desc)  )
            except ValueError, e : 
                errors.append( ('color%d'%i, "Invalid color: %s" % color) )
    
    if form["color_scheme"].value == 'color_custom' :
        logooptions.color_scheme =  custom
    else :
        try :
            logooptions.color_scheme = form["color_scheme"].get_value()
        except ValueError, err :
            errors.append(err.args)            

    sequences = None

    # FIXME: Ugly fix: Must check that sequence_file key exists
    # FIXME: Sending malformed or missing form keys should not cause a crash
    # sequences_file = form["sequences_file"]
    if form_values.has_key("sequences_file") :
        sequences = form_values.getvalue("sequences_file") 
        assert type(sequences) == str

    if not sequences or len(sequences)  ==0:
        sequences = form["sequences"].get_value()
    
    if not sequences or len(sequences)  ==0:
        errors.append( ("sequences", "Please enter a multiple-sequence alignment in the box above, or select a file to upload."))
  


    # If we have uncovered errors or we want the chance to edit the logo 
    # ("cmd_edit" command from examples page) then we return the form now.
    # We do not proceed to the time consuming logo creation step unless
    # required by a 'create' or 'validate' command, and no errors have been
    # found yet.
    if form_values.has_key("cmd_edit") or errors :
        send_form(controls, errors, htdocs_directory)
        return    
                

    # We write the logo into a local buffer so that we can catch and
    # handle any errors. Once the "Content-Type:" header has been sent
    # we can't send any useful feedback
    logo = StringIO()
    try :
        comp = form["composition"].get_value()
        percentCG = form["percentCG"].get_value()
        seqs = weblogo.read_seq_data(StringIO( sequences), alphabet=logooptions.alphabet)
        if comp=='percentCG': comp = str(percentCG/100)
        prior = weblogo.parse_prior(comp, seqs.alphabet)
        data = weblogo.LogoData(seqs, prior) 
        logoformat =  weblogo.LogoFormat(data, logooptions)
        format = form["format"].value
        weblogo.formatters[format](data, logoformat, logo)            
    except ValueError, e :
        errors.append( e.args )
    except RuntimeError, e :
        errors.append( e.args )
              
    if form_values.has_key("cmd_validate") or errors :
        send_form(controls, errors, htdocs_directory) 
        return    
 
 
    #
    #  RETURN LOGO OVER HTTP
    #

    print "Content-Type:", mime_type[format]
        
    # Content-Disposition: inline       Open logo in browser window
    # Content-Disposition: attachment   Download logo
    # print 'Content-Disposition: inline; filename="logo.%s"' % extension[format]        
    print 'Content-Disposition: attachment; filename="logo.%s"' % extension[format]        
        
    # Seperate header from data
    print 
        
    # Finally, and at last, send the logo.
    print logo.getvalue()        

  
def send_form(controls, errors=[], htdocs_directory=None) :
    if htdocs_directory is None :
        htdocs_directory = os.path.join(
            os.path.dirname(__file__, "weblogo_htdocs") )

    subsitutions = {}
    subsitutions["version"] = weblogo.release_description 
    
    for c in controls :
        if c.options :
            for opt in c.options :
                subsitutions[opt.replace('/','_')] = ''
            subsitutions[c.value.replace('/','_')] = 'selected'
        else :
            value = c.value
            if value == None : value = 'auto'
            if value=='true':
                subsitutions[c.name] = 'checked'
            elif type(value)==bool :
                if value :
                    subsitutions[c.name] = 'checked'
                else :
                    subsitutions[c.name] = ''
            else :
                subsitutions[c.name] = str(value)
        subsitutions[c.name+'_err']  = ''
            
    if errors :
        error_message = []
        for e in errors :
            if type(e) is str :
                msg = e
            elif len(e)==2:
                subsitutions[e[0]+"_err"] = "class='error'"    
                msg = e[1]
            else :
                msg = e[0]


            error_message +=  "ERROR: " 
            error_message +=  msg
            error_message += ' <br />'
            
        error_message += \
            "<input style='float:right; font-size:small' type='submit' name='cmd_validate' value='Clear Error' /> "
        subsitutions["error_message"] = ''.join(error_message)
    else :
        subsitutions["error_message"] = ""
    
        
    template = resource_string("create_html_template.html", htdocs_directory)
    html = Template(template).safe_substitute(subsitutions) #FIXME

    print "Content-Type: text/html\n\n"
    print html

    # DEBUG
    # keys = subsitutions.keys()
    # keys.sort()
    # for k in keys :
    #    print k,"=", subsitutions[k], " <br />" 

    #for k in controls :
    #    print k.name,"=", k.get_value(), " <br />" 



if __name__=="__main__" :
    main()



