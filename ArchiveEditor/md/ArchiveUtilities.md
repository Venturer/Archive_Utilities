# Help for Archive Utilities 3 - Introduction

## Why use the Archive Utilities?

The **Minos** contest logger has the facility to load an archive file containing Callsigns, Locators, Exchanges and other information on past contacts.

You can get Minos from: [http://minos.sourceforge.net/history.html](http://minos.sourceforge.net/history.html)

These files normally have the extension **.csl** and are based on comma separated variable files.

The *Archive Utilities* allow you to create and manage these files. The archives can be created and updated from the **.edi** contest entry files produced by **Minos**. The **.edi** files can also be checked against an archive.

## The Archive Utilities Suite comprises:

+ **Archive Maker**. Use this to create a new blank archive or to to add a **.edi** file or files to an *existing* archive. [Click here for Archive Maker help](ArchiveMaker.html)
+ **Archive Checker**. Use this to check a **.csl** archive you have *already* created to check its contents for possible errors that may have crept into it. [Click here for help](ArchiveChecker.html)
+ **Merge Archives**. Use this to merge two archives you may have created into one archive file. [Click here for help](MergeArchives.html)
+ **Archive Editor**. Use this to edit an archive. Using this utility helps to preserve the integrity and format of the file. [Click here for help](ArchiveEditor.html)
+ **Contest Reporter**. Use this to check a **.edi** file against an archive for possible typographic mistakes (such as typing G9BAC instead of G9ABC). [Click here for help](ContestReporter.html)
!+notes
## Notes

Each utility has its own detailed help.

Remember people do change QTH and change callsign, particularly from Foundation to Intermediate to Full, and good locations are also used by multiple stations, sometimes even at the same time!

**Whether a problem exists is entirely up to your judgement.**

Date format is: **yyyy/mm/dd**

*Right click* on the text displays for an edit menu which will allow you to cut and paste the report into another document.

`<a name="Changes" /a>`
## Changes from Version 2

+ Now built as a 32 bit windows application that no longer needs .NET to be installed. Some cosmetic changes result from this.
+ The utilities are now started from a single launcher application.
+ An Archive Editor is now included.
+ The window positions and sizes are saved when closed and restored when opened again.
+ Re-written using Python 3 and the Qt 5 framework.
+ The Python 3 source files are included in the **sources** sub folder of the install folder. They are released under the terms of the GNU General Public License.

## Terms of use

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS **AS IS** AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
