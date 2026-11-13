// Check the exact SESSION 141 GUI password path on real Windows:
// QInputDialog::getText -> QString -> QString::toUtf8 -> PBKDF2 -> AES-GCM.
// Use existing GitHub secret and real published packs, never log password.
#include "MemsDocumentaryEncryptedPack.h"
#include <QApplication>
#include <QDialog>
#include <QFile>
#include <QFileInfo>
#include <QInputDialog>
#include <QLineEdit>
#include <QTemporaryDir>
#include <QTest>
#include <QTimer>
#include <QString>
#include <cstdio>

static bool readThroughSessionDialog(
    const QString &secret,bool viaKeys,QString *received)
{
    bool sawPasswordField=false;
    bool error=false;
    QTimer::singleShot(0,[&](){
        auto *dialog=qobject_cast<QInputDialog *>(QApplication::activeModalWidget());
        if(!dialog){
            error=true;
            std::fprintf(stderr,"PASSWORD_DIALOG_NOT_OPEN\n");
            return;
        }
        QLineEdit *field=dialog->findChild<QLineEdit *>();
        if(!field || field->echoMode()!=QLineEdit::Password){
            error=true;
            dialog->reject();
            return;
        }
        sawPasswordField=true;
        field->setFocus();
        if(viaKeys){
            // Qt synthesizes keys, including special and Unicode characters,
            // through the very QLineEdit that SESSION uses.
            QTest::keyClicks(field,secret,0);
        }else{
            // Simulate paste/input-method insertion of the original secret.
            field->insert(secret);
        }
        dialog->accept();
    });
    bool accepted=false;
    *received=QInputDialog::getText(nullptr,
        QStringLiteral("Autorisation d'installation"),
        QStringLiteral("Mot de passe donné par l'administrateur :"),
        QLineEdit::Password,QString(),&accepted);
    if(error || !sawPasswordField || !accepted || received->isEmpty()){
        std::fprintf(stderr,"PASSWORD_DIALOG_INPUT_UNAVAILABLE\n");
        return false;
    }
    if(*received!=secret){
        std::fprintf(stderr,viaKeys?
            "PASSWORD_CHARACTER_CHANGED_BY_QT_KEY_INPUT\n":
            "PASSWORD_CHARACTER_CHANGED_BY_QT_PASTE_INPUT\n");
        return false;
    }
    std::fprintf(stdout,viaKeys?
        "PASSWORD_QINPUTDIALOG_KEY_INPUT_EXACT_MATCH_PASS\n":
        "PASSWORD_QINPUTDIALOG_PASTE_INPUT_EXACT_MATCH_PASS\n");
    return true;
}

int main(int argc,char **argv)
{
    QApplication app(argc,argv);
    if(argc!=3){
        std::fprintf(stderr,"REQUIRES_FR_AND_EN_PUBLISHED_PACKS\n");
        return 1;
    }
    const QString secret=qEnvironmentVariable("MEMS_DOCUMENTARY_PUBLISH_PASSWORD");
    if(secret.size()<12){
        std::fprintf(stderr,"PUBLISHER_SECRET_NOT_CONFIGURED\n");
        return 2;
    }
    QTemporaryDir temp;
    if(!temp.isValid())return 3;
    QString guiSecret,typedSecret;
    if(!readThroughSessionDialog(secret,false,&guiSecret))
        return 4;
    if(!readThroughSessionDialog(secret,true,&typedSecret))
        return 5;
    if(guiSecret.toUtf8()!=secret.toUtf8() ||
       typedSecret.toUtf8()!=secret.toUtf8()){
        std::fprintf(stderr,"PASSWORD_UTF8_ROUNDTRIP_MISMATCH\n");
        return 6;
    }
    // The SAME C++ production decoder invoked from SESSION 141.
    const QStringList langs={QStringLiteral("fr"),QStringLiteral("en")};
    for(int i=0;i<2;++i){
        const QString pack=QString::fromLocal8Bit(argv[i+1]);
        const QString zip=temp.filePath(langs.at(i)+QStringLiteral(".zip"));
        const QString failure=MemsDocumentaryEncryptedPack::decryptToZip(
            pack,typedSecret,zip);
        if(!failure.isEmpty()){
            std::fprintf(stderr,"REAL_%s_GUI_PASSWORD_AES_GCM_REJECTED\n",
                         qPrintable(langs.at(i)));
            return 7;
        }
        QFile file(zip);
        if(!file.open(QIODevice::ReadOnly) ||
           file.read(4)!=QByteArray::fromHex("504b0304") ||
           QFileInfo(zip).size()<1024){
            std::fprintf(stderr,"REAL_%s_DECRYPTED_ZIP_INVALID\n",
                         qPrintable(langs.at(i)));
            return 8;
        }
        std::fprintf(stdout,"REAL_%s_GUI_PASSWORD_AES_GCM_PASS\n",
                     qPrintable(langs.at(i)));
    }
    guiSecret.fill(QChar(' '));
    typedSecret.fill(QChar(' '));
    std::fprintf(stdout,"SESSION_141_GUI_PASSWORD_ROUNDTRIP_AND_FR_EN_PASS\n");
    return 0;
}
