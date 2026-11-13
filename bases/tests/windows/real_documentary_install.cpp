#include "MemsDocumentaryLocalInstaller.h"
#include "MemsDocumentaryPackCatalog.h"

#include <QCoreApplication>
#include <QFileInfo>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QStandardPaths>
#include <QTemporaryDir>
#include <QVariant>
#include <cstdio>

static bool inspect(const QString &language, int documents, int pages,
                    int entries, int images)
{
    const QString path=MemsDocumentaryPackCatalog::installedDatabasePath(language);
    if(!QFileInfo::exists(path))
        return false;
    const QString connection=QStringLiteral("TEST_%1").arg(language);
    bool ok=false;
    {
        QSqlDatabase db=QSqlDatabase::addDatabase(QStringLiteral("QSQLITE"),connection);
        db.setConnectOptions(QStringLiteral("QSQLITE_OPEN_READONLY"));
        db.setDatabaseName(path);
        if(db.open()){
            QSqlQuery q(db);
            if(language==QStringLiteral("fr")){
                ok=q.exec(QStringLiteral(
                    "SELECT (SELECT COUNT(*) FROM documentary_documents),"
                    "(SELECT COUNT(*) FROM documentary_pages),"
                    "(SELECT COUNT(*) FROM documentary_entries),"
                    "(SELECT COUNT(*) FROM documentary_images)")) &&
                    q.next() && q.value(0).toInt()==documents &&
                    q.value(1).toInt()==pages &&
                    q.value(2).toInt()==entries &&
                    q.value(3).toInt()==images;
            }else{
                ok=q.exec(QStringLiteral(
                    "SELECT (SELECT COUNT(*) FROM source_documents),"
                    "(SELECT COUNT(*) FROM source_page_discovery),"
                    "(SELECT COUNT(*) FROM procedure_steps),"
                    "(SELECT COUNT(*) FROM illustrations)")) &&
                    q.next() && q.value(0).toInt()==documents &&
                    q.value(1).toInt()==pages &&
                    q.value(2).toInt()==entries &&
                    q.value(3).toInt()==images;
            }
            db.close();
        }
    }
    QSqlDatabase::removeDatabase(connection);
    return ok;
}

int main(int argc,char **argv)
{
    QCoreApplication app(argc,argv);
    QCoreApplication::setOrganizationName(QStringLiteral("MEMS_TEST"));
    QCoreApplication::setApplicationName(QStringLiteral("REAL_DOCUMENTARY_PACK_TEST"));
    QStandardPaths::setTestModeEnabled(true);
    if(argc!=3){
        std::fprintf(stderr,"EXPECTED_TWO_PACK_PATHS\n");
        return 1;
    }
    const QString password=qEnvironmentVariable("MEMS_DOCUMENTARY_PUBLISH_PASSWORD");
    if(password.size()<12){
        std::fprintf(stderr,"PUBLISHER_PASSWORD_NOT_CONFIGURED\n");
        return 1;
    }
    QTemporaryDir temporary;
    if(!temporary.isValid()){
        std::fprintf(stderr,"TEMP_DIR_NOT_AVAILABLE\n");
        return 1;
    }
    const QString frError=MemsDocumentaryLocalInstaller::installEncrypted(
        QString::fromLocal8Bit(argv[1]),QStringLiteral("fr"),password);
    if(!frError.isEmpty()){
        std::fprintf(stderr,"FR_INSTALL_FAILED %s\n",qPrintable(frError));
        return 1;
    }
    if(!inspect(QStringLiteral("fr"),2,391,6387,345)){
        std::fprintf(stderr,"FR_INSTALLED_DATABASE_INVALID\n");
        return 1;
    }
    std::puts("REAL_FRENCH_ENCRYPTED_INSTALL_PASS_2_MANUALS");

    const QString enError=MemsDocumentaryLocalInstaller::installEncrypted(
        QString::fromLocal8Bit(argv[2]),QStringLiteral("en"),password);
    if(!enError.isEmpty()){
        std::fprintf(stderr,"EN_INSTALL_FAILED %s\n",qPrintable(enError));
        return 1;
    }
    if(!inspect(QStringLiteral("en"),1,482,5055,316)){
        std::fprintf(stderr,"EN_INSTALLED_DATABASE_INVALID\n");
        return 1;
    }
    std::puts("REAL_ENGLISH_ENCRYPTED_INSTALL_PASS_1_MANUAL");
    std::puts("WINDOWS_DOCUMENTARY_BOTH_REAL_PACKS_VERIFIED_NO_PUBLICATION");
    return 0;
}
