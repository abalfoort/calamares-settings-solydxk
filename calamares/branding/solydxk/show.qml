/* === This file is part of Calamares - <https://calamares.io> ===
 *
 *   SPDX-FileCopyrightText: 2015 Teo Mrnjavac <teo@kde.org>
 *   SPDX-FileCopyrightText: 2018 Adriaan de Groot <groot@kde.org>
 *   SPDX-License-Identifier: GPL-3.0-or-later
 *
 *   Calamares is Free Software: see the License-Identifier above.
 *
 */

import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation
    
    function nextSlide() {
        presentation.goToNextSlide();
        console.log("Current slide: %1".arg(presentation.currentSlide));
    }

    Timer {
        id: advanceTimer
        interval: 10000
        running: false
        repeat: true
        onTriggered: nextSlide()
    }
    
    Image {
        source: "background.png"
        anchors.fill: parent
    }

    Slide {
        anchors.fill: parent

        Text {
            text: qsTr("<h3>Thank you for choosing SolydXK</h3><br />" +
                            "You've chosen a Linux distribution that is:<br />" +
                            "<ul><li>Secure and stable</li><li>Fast and responsive</li><li>Desktop-ready</li></ul><br />" +
                            "Enjoy this new release and thank you for choosing SolydXK.<br /><br />" +
                            "The installation takes 15-30 minutes, depending on your settings.")
            anchors.fill: parent
            anchors.rightMargin: 300
            anchors.leftMargin: 20
            anchors.bottomMargin: 20
            anchors.topMargin: 20
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: parent.width * .020
            color: '#4c4c4c'
        }
    }
    
    Slide {
        anchors.fill: parent

        Text {
            text: qsTr("<h3>Standing on the shoulders of Giants</h3><br />" +
                            "SolydXK is a Debian-based GNU/Linux distribution derived from and compatible with Debian.<br /><br />" +
                            "SolydXK uses either the lightweight Xfce desktop for SolydX or the highly configurable and stunningly appealing KDE desktop for SolydK.<br /><br />" +
                            "Our innovations, the rapid development of Debian and the huge Debian package selection make SolydXK one of the most attractive desktop operating systems available to home users.")
            anchors.fill: parent
            anchors.rightMargin: 300
            anchors.leftMargin: 20
            anchors.bottomMargin: 20
            anchors.topMargin: 20
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: parent.width * .020
            color: '#4c4c4c'
        }
    }
    
    Slide {
        anchors.fill: parent

        Text {
            text: qsTr("<h3>Out of the box</h3><br />" +
                            "Firefox, Thunderbird, and LibreOffice come pre-installed in SolydXK, so you can get started immediately with the desktop and the Internet.<br /><br />" +
                            "Unlike other Linux distributions SolydXK is also ready to play your music, internet videos and more.<br /><br />" +
                            "A wide variety of software can be installed with a click of the mouse.<br /><br />" +
                            "SolydXK is compatible with most popular file formats such as: docx, xlsx, doc, xls, pdf, zip, rar, mp3, mpg, and many more.")
            anchors.fill: parent
            anchors.rightMargin: 300
            anchors.leftMargin: 20
            anchors.bottomMargin: 20
            anchors.topMargin: 20
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: parent.width * .020
            color: '#4c4c4c'
        }
    }
    
    Slide {
        anchors.fill: parent

        Text {
            text: qsTr("<h3>Office tools are ready to use as soon as you install SolydXK</h3><br />" +
                            "LibreOffice, a powerful office software suite, comes built into SolydXK.<br /><br />" +
                            "LibreOffice is very easy to learn and use.<br /><br />" +
                            "You can use it to create letters, presentations and spreadsheets, as well as diagrams and databases.<br /><br />" +
                            "LibreOffice uses the standard OpenDocument format and it works with documents from other popular office applications including WordPerfect and Microsoft Office.")
            anchors.fill: parent
            anchors.rightMargin: 300
            anchors.leftMargin: 20
            anchors.bottomMargin: 20
            anchors.topMargin: 20
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: parent.width * .020
            color: '#4c4c4c'
        }
    }
    
    Slide {
        anchors.fill: parent

        Text {
            text: qsTr("<h3>An alternative to mainstream operating systems</h3><br />" +
                            "SolydXK is easy to use, powerful and configurable.<br /><br />" +
                            "SolydXK is safe and stable. Unlike other operating systems, it is not prone to computer viruses or spyware, it does not suffer from disk fragmentation, and it has no registry that requires periodic cleaning.<br /><br />" +
                            "SolydXK can detect other operating systems and install itself beside them.You can choose which operating system to launch when you start the computer.")
            anchors.fill: parent
            anchors.rightMargin: 300
            anchors.leftMargin: 20
            anchors.bottomMargin: 20
            anchors.topMargin: 20
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: parent.width * .020
            color: '#4c4c4c'
        }
    }
    
    Slide {
        anchors.fill: parent

        Text {
            text: qsTr("<h3>Safe updates</h3><br />" +
                            "Some operating systems make updating your system harder than it really needs to be. SolydXK thinks upgrades should be quick and easy, and then get out of the way.<br /><br />" +
                            "The Update Manager sits discreetly in your system tray and lets you know when updates are available. You don't have to apply updates when you don't want to. The Update Manager won't pop up or annoy you in any way.<br /><br />" +
                            "All updated files are maintained and closely checked by trusted developers and maintainers.<br /><br />" +
                            "All files are stored in special secure repositories for your use.<br /><br />" +
                            "The security repository is synchronized daily.")
            anchors.fill: parent
            anchors.rightMargin: 300
            anchors.leftMargin: 20
            anchors.bottomMargin: 20
            anchors.topMargin: 20
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: parent.width * .020
            color: '#4c4c4c'
        }
    }
    
    Slide {
        anchors.fill: parent

        Text {
            text: qsTr("<h3>A great community</h3><br />" +
                            "SolydXK users are happy to share their passion and enthusiasm and are eager to help. Don't hesitate to ask questions on the forums or to get involved in the community.<br /><br />" +
                            "Send us your feedback and tell us about your experience. We'll listen to your ideas and use them to further improve SolydXK.")
            anchors.fill: parent
            anchors.rightMargin: 300
            anchors.leftMargin: 20
            anchors.bottomMargin: 20
            anchors.topMargin: 20
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: parent.width * .020
            color: '#4c4c4c'
        }
    }

    // When this slideshow is loaded as a V1 slideshow, only
    // activatedInCalamares is set, which starts the timer (see above).
    //
    // In V2, also the onActivate() and onLeave() methods are called.
    // These example functions log a message (and re-start the slides
    // from the first).
    function onActivate() {
        presentation.currentSlide = 0;
        advanceTimer.running = true
        console.log("QML Component (solydxk slideshow) activated");
    }
    
    function onLeave() {
        console.log("QML Component (default slideshow) deactivated");
    }

}
