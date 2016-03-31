package main

import (
    "fmt"
    "strings"
    "encoding/json"
    "encoding/pem"
    "encoding/base64"
    "regexp"
    "time"
    "io/ioutil"
    "os/exec"
    "bytes"
    "crypto"
    "crypto/rsa"
    "crypto/sha1"
    "crypto/x509"

    core "github.com/ipfs/go-ipfs/core"
    corenet "github.com/ipfs/go-ipfs/core/corenet"
    fsrepo "github.com/ipfs/go-ipfs/repo/fsrepo"
    httpApi "github.com/42cc/go-ipfs-api"

    "github.com/golang-samples/revel/src/code.google.com/p/go.net/context"
)

const (
    protocolAddress  = "/42coffeecupfs/e-proxy-voting"
    shellUrl         = "localhost:5401"
    encoding         = "json"
    blacklist        = "blacklist.pub"
    pythonScriptName = "get_list.py"
)

type ClientData struct {
    Hash string
}

type IpfsObject struct {
    Data SignedBulletin
}

type Bulletin struct {
    Voting string `json:"voting"`
    Vote string `json:"vote"`
    Voter string `json:"voter"`
    Datetime string `json:"datetime"`
    PublicKey string `json:"publickey"`
}

type SignedBulletin struct {
    Bulletin Bulletin `json:"bulletin"`
    Signature string  `json:"signature"`
}

func GetKey(filename string) string {
    key, err := ioutil.ReadFile(filename)
    if err != nil {
        panic(err)
    }
    return string(key)
}

func DataStr2JSON(bulletin string) string {
    r := strings.NewReplacer(
            `"data":"{`, `"data":{`,
            `\"`, `"`,
            `}","links"`, `},"links"`)
    bulletinJSON := r.Replace(bulletin)
    return bulletinJSON
}

func BulletinJSON2Obj(bulletin string) (*IpfsObject, error) {
    // json to struct
    ipfsObj := &IpfsObject{}
    err := json.Unmarshal([]byte(bulletin), &ipfsObj)
    if err != nil {
        fmt.Println(err)
        return nil, err
    }
    return ipfsObj, nil
}

func HashValidation(hash string) string {
    // check length
    if len(hash) != 46 {
        return "length of hash must be 46 characters"
    }
    // check whether in the hash only from numbers and letters
    re := regexp.MustCompile(`\w+`)
    match := re.FindStringSubmatch(hash)
    if len(match[0]) != 46 {
        return "hash must have only from numbers and letters"
    }

    // excludes characters
    if strings.Contains(hash, "0") {
        return "hash should not have '0'"
    }
    if strings.Contains(hash, "O") {
        return "hash should not have 'O'"
    }
    if strings.Contains(hash, "I") {
        return "hash should not have 'I'"
    }
    if strings.Contains(hash, "l") {
        return "hash should not have 'l'"
    }

    return "valid"
}

func DateValidation(date string) string {
    format := "2006-02-01T15:04:05.000Z"
    _, err := time.Parse(format, date)

    if err != nil {
        return "Datetime is not valid"
    }
    return "valid"
}

func SignatureValidation(signature string) string {
    if len(signature) <= 10 {
        return "Signature must be longer then 10"
    }
    if signature[len(signature)-2:] != "==" {
        return "Signature must be end with '=='"
    }
    re := regexp.MustCompile(`(\w|\+|\/)+`)
    match := re.FindStringSubmatch(signature)
    if len(match[0]) != (len(signature) - 2) {
        return "Signature must have only from numbers, letters and '/+'"
    }
    return "valid"
}

func BulletinValidation(bulletin *IpfsObject) string {
    errors := ""
    // validations for hashes
    resultVotingHash := HashValidation(bulletin.Data.Bulletin.Voting)
    if resultVotingHash != "valid" {
        errors += "Voting " + resultVotingHash + "\n"
    }
    resultVoteHash := HashValidation(bulletin.Data.Bulletin.Vote)
    if resultVoteHash != "valid" {
        errors += "Vote " + resultVoteHash + "\n"
    }
    resultVoterHash := HashValidation(bulletin.Data.Bulletin.Voter)
    if resultVoterHash != "valid" {
        errors += "Voter " + resultVoterHash + "\n"
    }

    // validation for date
    resultDatetime := DateValidation(bulletin.Data.Bulletin.Datetime)
    if resultDatetime != "valid" {
        errors += resultDatetime + "\n"
    }

    // validation for signature
    resultSignature := SignatureValidation(bulletin.Data.Signature)
    if resultSignature != "valid" {
        errors += resultSignature + "\n"
    }
    signIsTrue, _ := CheckSignature(bulletin)
    if !signIsTrue {
        errors += "Invalid signature for bulletin.\n"
    }

    if errors != "" {
        return errors
    }

    return "valid"
}

func CheckSignature(bulletinObj *IpfsObject) (bool, string) {
    bulletin, err := json.Marshal(bulletinObj.Data.Bulletin)
    if err != nil {
        return false, err.Error()
    }
    signature, err := base64.StdEncoding.DecodeString(bulletinObj.Data.Signature)
    if err != nil {
        return false, err.Error()
    }
    pubKey := strings.Replace(bulletinObj.Data.Bulletin.PublicKey, "_", "\n", -1)
 
    // Parse public key into rsa.PublicKey
    PEMBlock, _ := pem.Decode([]byte(pubKey))
    if PEMBlock == nil {
        return false, "Could not parse Public Key PEM"
    }
    if PEMBlock.Type != "PUBLIC KEY" {
        return false, "Found wrong key type"
    }
    pubkey, err := x509.ParsePKIXPublicKey(PEMBlock.Bytes)
    if err != nil {
        return false, err.Error()
    }

    // compute the sha1
    h := sha1.New()
    h.Write([]byte(bulletin))

    // Verify
    err = rsa.VerifyPKCS1v15(pubkey.(*rsa.PublicKey), crypto.SHA1, h.Sum(nil), signature)
    if err != nil {
        return false, err.Error()
    }

    // It verified!
    return true, ""
}

func main() {
    // Basic ipfsnode setup
    r, err := fsrepo.Open("~/.ipfsEvoxHost")
    if err != nil {
        panic(err)
    }

    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    cfg := &core.BuildCfg{
        Repo:   r,
        Online: true,
    }

    nd, err := core.NewNode(ctx, cfg)
    if err != nil {
        panic(err)
    }

    list, err := corenet.Listen(nd, protocolAddress)
    if err != nil {
        panic(err)
    }
    fmt.Printf("I am peer: %s\n", nd.Identity.Pretty())

    for {
        con, err := list.Accept()
        if err != nil {
            fmt.Println(err)
            return
        }
        defer con.Close()

        buf := make([]byte, 256)
        n, err := con.Read(buf)
        if err != nil {
            fmt.Println(err)
        }

        // save data from client request
        clientData := &ClientData{}
        err = json.Unmarshal([]byte(buf[:n]), &clientData)
        if err != nil {
            fmt.Println(err)
        }

        // get bulletin from ipfs
        s := httpApi.NewShell(shellUrl)
        bulletinStr, err := s.GetObject(clientData.Hash)
        if err != nil {
            fmt.Println(err)
        }

        // CREATE BULLETIN OBJECT FROM BULLETIN STR
        bulletinIpfsJSON := DataStr2JSON(bulletinStr)
        bulletinIpfsObj, err := BulletinJSON2Obj(bulletinIpfsJSON)
        if err != nil {
            fmt.Println(err)
        }

        listOfBKeys := strings.Split(GetKey(blacklist), "\n\n")
        pubKey := strings.Replace(bulletinIpfsObj.Data.Bulletin.PublicKey, "_", "\n", -1)
        inBlasklist := false
        for _, BKey := range listOfBKeys {
            if BKey == pubKey {
                fmt.Fprintln(con, "This user is in a blacklist")
                inBlasklist = true
                break
            }
        }

        resultValidation := BulletinValidation(bulletinIpfsObj)
        // if bulletin is not valid then return errors to client
        if resultValidation != "valid" {
            fmt.Fprintln(con, resultValidation)
        }

        if !inBlasklist && resultValidation == "valid" {
            // call python script for update list of bulletins
            cmd := exec.Command(pythonScriptName, "-b", clientData.Hash)
            var out bytes.Buffer
            var stderr bytes.Buffer
            cmd.Stdout = &out
            cmd.Stderr = &stderr
            err := cmd.Run()
            // return output to client
            if err != nil {
                fmt.Fprintln(con, fmt.Sprint(err) + ": " + stderr.String())
            } else {
                fmt.Fprintln(con, out.String())
            }
        }
    }
}