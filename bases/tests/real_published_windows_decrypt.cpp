// Runs the production SESSION AES-GCM decoder against encrypted FR/EN release
// assets using the publisher secret, without printing or storing that secret.
// The decrypted ZIP exists only in the CI temporary directory.
#include "MemsDocumentaryEncryptedPack.h"
#include <QCoreApplication>
#include <QByteArray>
#include <QCryptographicHash>
#include <QFile>
#include <QFileInfo>
#include <QTemporaryDir>
#include <QString>
#include <cstdio>

int main(int argc,char **argv)
{
    QCoreApplication app(argc,argv);
    if(argc!=3){
        std::fprintf(stderr,"USAGE: native_published_pack_test FR.encrypted EN.encrypted\n");
        return 1;
    }
    const QString password=qEnvironmentVariable("MEMS_DOCUMENTARY_PUBLISH_PASSWORD");
    if(password.size()<12){
        std::fprintf(stderr,"SECRET_NOT_CONFIGURED\n");
        return 2;
    }
    QTemporaryDir working;
    if(!working.isValid())return 3;
    const QStringList languages={QStringLiteral("fr"),QStringLiteral("en")};
    for(int i=0;i<2;++i){
        const QString encrypted=QString::fromLocal8Bit(argv[i+1]);
        const QString zip=working.filePath(languages.at(i)+QStringLiteral(".zip"));
        const QString failure=MemsDocumentaryEncryptedPack::decryptToZip(
            encrypted,password,zip);
        if(!failure.isEmpty()){
            std::fprintf(stderr,"PRODUCTION_DECRYPT_FAILED_%s: %s\n",
                         qPrintable(languages.at(i)),qPrintable(failure));
            return 4;
        }
        QFile plaintext(zip);
        if(!plaintext.open(QIODevice::ReadOnly)||
           plaintext.read(4)!=QByteArray::fromHex("504b0304")||
           QFileInfo(zip).size()<1024){
            std::fprintf(stderr,"PRODUCTION_ZIP_INVALID_%s\n",
                         qPrintable(languages.at(i)));
            return 5;
        }
        plaintext.close();
        std::fprintf(stdout,"REAL_%s_GCM_DECRYPT_PASS_BYTES=%lld\n",
            qPrintable(languages.at(i)),
            static_cast<long long>(QFileInfo(encrypted).size()));
    }
    std::fprintf(stdout,"REAL_PUBLISHED_PACKS_NATIVE_PASSWORD_MATCH_PASS\n");
    return 0;
}
