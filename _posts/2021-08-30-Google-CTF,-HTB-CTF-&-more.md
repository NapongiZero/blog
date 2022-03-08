---
title: Google CTF, HTB CTF & more 
published: true
---

Since my last post, I had the pleasure to participate in a lot of [CTFs](https://www.youtube.com/watch?v=8ev9ZX9J45A). 

In this post, I'll be covering a few challenges that I encountered and deemed interesting enough to share. 

The first section (covering the first challenge) will be a complete write-up, the 2nd will contain a more high-level write-up and the 3rd will be left as a challenge for the reader. 


# Table of Contents

- [Table of Contents](#table-of-contents)
- [HTB Business CTF 2021 - DFIR](#htb-business-ctf-2021---dfir)
  - [Malicious Scheduled Task](#malicious-scheduled-task)
  - [svchost.exe - Malware Analysis](#svchostexe---malware-analysis)
- [Google CTF 2021 - CPP](#google-ctf-2021---cpp)
- [C2C Qualifier - Ghost in the Website](#c2c-qualifier---ghost-in-the-website)

<br>

# HTB Business CTF 2021 - DFIR

[HTB](https://www.hackthebox.eu/) is a fantastic platform to tackle on challenges and unique Fullpwn boxes. 
Besides their main platform, they also have a [CTF platform](https://ctf.hackthebox.eu/).
This particular CTF sure was a blast, as it mainly focused on real-world challenges.

This 3-day CTF included multiple categories:

```
Fullpwn | Web | Pwn | Reversing | Crypto | Forensics | Misc & Cloud.
```

My favorite challenge from this CTF was "DFIR" from the Forensics category. I definitely learned
quite a bit from it, as I'm not an expert on forensics.

The challenge intro was as following:

![](assets/HTB_CTF_2021/dfir_intro.png)

## Malicious Scheduled Task

Basically, we have a virtual machine (.ova) that has some weird PowerShell windows popping up at startup.

Nothing really caught my eye during some manual reconnaissance around the system.

Later on, I thought to myself that since the PowerShell popped up right when I logged on, that there might be a scheduled task running in the background at startup.

Task Scheduler indeed shows signs of a malicious PowerShell, which is triggered at log on:
![](assets/HTB_CTF_2021/taskScheduler.png)

I exported the task to an .xml file to take a closer look:

![](assets/HTB_CTF_2021/powershell_cmd.png)

It seems that the PowerShell task is grabbing a registry key with a base64 value.  
I headed over to the registry in order to copy the value, and decode it myself. 
(Although in hindsight, I could've just used the same code from the script arguments… oh well)

![](assets/HTB_CTF_2021/registryValue.png)

I decoded it locally:

![](assets/HTB_CTF_2021/decodeRegValue.png)

And… Yay! We got the flag! That was rather easy!
Waitt... this isn't the full flag. Seems like the flag was split… hopefully only to two parts >.<

I'll be honest here and say that I didn't get the 2nd part of the flag during the CTF. There were other challenges that needed to be solved.
After the CTF, I came back to the challenge from where I last picked off. I took my time to solve it without stressing for points & bloods.

## svchost.exe - Malware Analysis

Anyway, with no hints or nudges on how to continue, I decided to look around the system again. 
This time around, I decided to use "[Everything](https://www.voidtools.com/)" to navigate the system with ease. 
I filtered for ".exe" files in different folders in order to find unusual executables.
I also used "[ProcessHacker](https://processhacker.sourceforge.io/)" to see if some processes have a high network/CPU usage and whatnot.

After a tedious long search I found this "svchost.exe" in a very irregular location in the file system:

![](assets/HTB_CTF_2021/bad_svchost.png)

I then threw it into VirusTotal and found out it was indeed malicious! Hurray?!:

![](assets/HTB_CTF_2021/virustotal.png)

Besides that, VirusTotal wasn't much help. 

I tried to execute the binary (in the already vulnerable VM) with ProcessHacker running in the background, but nothing seemed out of the ordinary.
Furthermore. I looked for embedded Unicode "[Strings](https://docs.microsoft.com/en-us/sysinternals/downloads/strings)" but the output was too large even when filtering with a minimum string length of 10.

I then dropped the binary into Ghidra. I checked the entry function, and then continued to "FUN_140001000" which contained some odd strings such as "_MEIPASS2".

![](assets/HTB_CTF_2021/meipass2.png)

A quick Google search reveals that "MEIPASS2" is an environment variable for the Pyinstaller package.
Meaning that this executable was most likely built with Pyinstaller. 

We can unpack the executable and get a hold of ```.pyc``` files. (.pyc files are the compiled bytecode of the Python source files)

An [answer on StackExchange](https://reverseengineering.stackexchange.com/a/164) explains how you can extract the .pyc code from the executable manually. Instead of doing it manually (which isn't much work really) I used a [script from GitHub](https://github.com/extremecoders-re/pyinstxtractor) which does it automatically: ```python pyinstxtractor.py svchost.exe```, resulting with the following .pyc files:

![](assets/HTB_CTF_2021/pyc.png)

As I mentioned, these are the compiled bytecode of the Python source files. We can take a look at the source code by 
decompiling them. I used [uncompyle6](https://pypi.org/project/uncompyle6/) to do it, but I tackled a problem... uncompyle6 only
worked on 4 out of the 6 files. "pyiboot01_bootstrap.pyc" & "logger.pyc" failed to decompile.

We all have these moments where we can't think straight, and this was definitely one of those times.
In order to fix the decompilation issue, I attempted unpacking the executable again, reinstalling uncompyle6 & even trying it on different Python versions... 
Instead, what I should've done in the first place is a simple file type check:

![](assets/HTB_CTF_2021/filepyc.png)

Ah! So "pyiboot01_bootstrap.pyc" & "logger.pyc" aren't valid .pyc files.

![](assets/HTB_CTF_2021/pyc_hexdump.png)

A hexdump shows that their magic number is faulty, and that's why they weren't classified as compiled bytecode. (started with ```\x61``` instead of ```\x42```)

In order to fix the first byte of the faulty files I used [Okteta](https://apps.kde.org/okteta/) but any hex-editor should work. 

![](assets/HTB_CTF_2021/okteta.png)

After saving the change, uncompyle6 successfully decompiled the files.
Taking a closer look at [logger.py](https://github.com/NapongiZero/blog/blob/master/assets/HTB_CTF_2021/logger.py) reveals that it's probably a keylogger, since it listens to keystrokes. They are then written to a file in APPDATA. Before writing to the file, the logged keystrokes are encrypted by using AES with hard-coded Key & IV.

![](assets/HTB_CTF_2021/encrypted_file.png)

The encrypted content:
![](assets/HTB_CTF_2021/encrypted_txt.png)

Since the key & IV are supplied, we can write a script that decrypts the encrypted text:

![](assets/HTB_CTF_2021/decrypt_script.png)

After decrypting the file, I got rid of most of the excess text such as "Key.space" & "Key.enter" as they clutter the file.
While cleaning up the file, I noticed a message from someone who used the computer before:

![](assets/HTB_CTF_2021/usr_pin.png)

The PIN completes our flag and successfully finishes the challenge.

HTB{1_c4n_S33_3v3ryTh1ng_3v3n_y0uR_P1N_50133700013}


<br>

# Google CTF 2021 - CPP

Google CTF is notoriously difficult. And this year was no different.

I went in solo, and I've spent the majority of my time on a challenge called "CPP".

The challenge intro was:
```
We have this program's source code, but it uses a strange DRM solution. Can you crack it?
```


Let's take a peak at the [source](https://github.com/google/google-ctf/blob/master/2021/quals/rev-cpp/attachments/cpp.c):

![](assets/googlectf2021/flag_input.png)  ![](assets/googlectf2021/char.png) ![](assets/googlectf2021/snipet2.png)

From this, we can infer that we need to input the flag at the start. Moreover, the code was mostly made out of preprocessor directives such as #defines, #ifndef & #if #else statements. 
Objectively, it seems that we can solve this with symbolic execution (which is why I decided to work on this challenge).
In order to gain more knowledge about the program, I decided to compile the program and execute it.

![](assets/googlectf2021/compileError.png)

It seems that our flag is undergoing weird validation tests while compiling the program, and that the program will only be compiled if we pass the validation. Nevertheless, the input that passes the validation is most likely the flag itself.
Having a closer look at the cpp.c file, I found these function-like macros:

![](assets/googlectf2021/funcMacro.png)

I then went on and tried to reverse engineer the code, but it was painful. (After the CTF, I was amazed to read a [write-up of 2 mad lads](https://github.com/cscosu/ctf-writeups/tree/master/2021/google_ctf/cpp) that actually did just that)

I was eager to try and solve this challenge with symbolic execution, But I just couldn't find a symbolic execution engine that can handle these preprocessor directives…

It then occurred to me that perhaps I could turn this ugly C code into Python code. If done correctly, one could easily use [Angr](http://angr.io/) or Z3 on it and solve the constraints. This turned out to be the more "sane" approach to solve this challenge. And since there are already some great write-ups on this challenge, I invite you to check out Zeyu's [solution](https://ctf.zeyu2001.com/2021/google-ctf-2021/cpp) for more on that approach. But before that, let me introduce the 3rd and last challenge for this post.

<br>

# C2C Qualifier - Ghost in the Website

When was the last time you did a good OSINT challenge? 
"Ghost in the Website" from C2C CTF-qualifier was very refreshing.

It was very enjoyable, and I invite you to give it a try.

The challenge description:

```deepnoobdev created his portfolio as a static website using a famous platform. Can you delve into its secrets?```

At the time of writing, the challenge is still up & running.

Go ahead and see if you can find the flag :)

<br>

Until next time~


