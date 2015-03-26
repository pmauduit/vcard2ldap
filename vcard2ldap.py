#!/usr/bin/python

import ldap
import string
import sys

import base64

import vobject

# Adapt here to point to your ldap directory
ldapCnx = ldap.initialize("ldap://localhost:10389")

# Put here a binddn which has rw access to your directory
ldapCnx.simple_bind_s("cn=user_admin,dc=example,dc=com","password")

# Edit here to indicate where to store the newly created users
ldapBaseDn = "dc=accounts,dc=example,dc=com"

vcfFile = open(sys.argv[1])
vc =  vobject.readComponents(vcfFile)

while True:
    try:
        cur = vc.next()

        ldapItem = [('objectClass',['top','person',
                        'organizationalPerson','inetOrgPerson'])]
        name = ""
        jpegPhoto = ""
        mail = ""
        cn = ""
        telNumber = ""

        # Iterating on each attributes
        for attribElem in cur.getChildren():

            if isinstance(attribElem.value, vobject.vcard.Name):
                name = attribElem.value.__str__()
                name = name.strip()
                cn = name.lower()
                cn = ' '.join(cn.split())
                givenName = attribElem.value.given
                sn = attribElem.value.family
                try:
                    ldapItem += [('cn', str(cn)), ('givenName', str(givenName)), ('sn', str(sn))]
                except UnicodeEncodeError:
                    print "Error decoding strings to ASCII, giving up on this record"

            if attribElem.name == 'PHOTO':
                jpegPhoto = attribElem.value
                ldapItem += [('jpegPhoto', jpegPhoto)]

            if attribElem.name == 'EMAIL':
                mail = attribElem.value
                ldapItem += [('mail', str(mail))]

            if attribElem.name == 'TEL':
                telNumber = attribElem.value
                ldapItem += [('telephoneNumber', str(telNumber))]

        # end iterating on attributes
        if cn == "":
            continue
        try:
            base_dn = 'cn=' + cn + ',' + ldapBaseDn
            ldapCnx.add_s(base_dn,ldapItem)
            print 'Added ' + cn
        except ldap.ALREADY_EXISTS:
            base_dn = 'cn='+ cn + ' DUPLICATED,' + ldapBaseDn
            ldapCnx.add_s(base_dn,ldapItem)
        except Exception:
            print 'ERROR : Cannot succeed in adding ' + name
    except StopIteration:
        break

vcfFile.close()
