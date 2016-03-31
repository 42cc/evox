package main

import (
    "fmt"
    "io/ioutil"
    "os"
    "time"
    "bytes"
    "strings"
    "encoding/json"
    "encoding/pem"
    "encoding/base64"
    "crypto"
    "crypto/rand"
    "crypto/rsa"
    "crypto/sha1"
    "crypto/x509"

    core "github.com/ipfs/go-ipfs/core"
    corenet "github.com/ipfs/go-ipfs/core/corenet"
    peer "gx/ipfs/QmUBogf4nUefBjmYjn6jfsfPJRkmDGSeMhNj4usRKq69f4/go-libp2p/p2p/peer"
    fsrepo "github.com/ipfs/go-ipfs/repo/fsrepo"
    httpApi "github.com/42cc/go-ipfs-api"

    "github.com/golang-samples/revel/src/code.google.com/p/go.net/context"
)

const (
    protocolAddress = "/42coffeecupfs/e-proxy-voting"
    shellUrl        = "localhost:5501"
    encoding        = "json"
)

type IpfsObject struct {
    Data string
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

// create ipfs object without links
func CreateIpfsObjectJson(data string) string {
    ipfsObject := IpfsObject{Data: data}

    ipfsObjectJson, err := json.Marshal(ipfsObject)
    if err != nil {
        panic(err)
    } 
    return string(ipfsObjectJson)
} 

func CreateBulletin(votingHash, voteHash, voterHash, nameOfPubKey string) Bulletin {
    pubKey := strings.Replace(GetKey(nameOfPubKey), "\n", "_", -1) // replace all line breaks on the spaces
    bulletinObj := Bulletin{
        Voting: votingHash,
        Vote: voteHash,
        Voter: voterHash,
        Datetime: time.Now().Format("2006-02-01T15:04:05.000Z"),
        PublicKey: pubKey,
    }
    return bulletinObj
}

func CreateSignedBulletin(bulletin Bulletin, privKeyPEM string) string {
    bulletinJson, err := json.Marshal(bulletin)
    if err != nil {
        panic(err)
    } 
    signature := base64.StdEncoding.EncodeToString(JSONSign(string(bulletinJson), privKeyPEM))

    signedBulletinObj := SignedBulletin{bulletin, signature}
    signedBulletinJson, err := json.Marshal(signedBulletinObj)
    if err != nil {
        panic(err)
    } 
    return string(signedBulletinJson)
}

func GetKey(filename string) string {
    key, err := ioutil.ReadFile(filename)
    if err != nil {
        panic(err)
    }
    return string(key)
}

func JSONSign(data, privKeyPEM string) []byte {
    // Parse private key into rsa.PrivateKey
    PEMBlock, _ := pem.Decode([]byte(privKeyPEM))
    if PEMBlock == nil {
        panic("Could not parse Private Key PEM")
    }
    if PEMBlock.Type != "RSA PRIVATE KEY" {
        panic("Found wrong key type")
    }
    privkey, err := x509.ParsePKCS1PrivateKey(PEMBlock.Bytes)
    if err != nil {
        panic(err)
    }

    // Compute the sha1
    h := sha1.New()
    h.Write([]byte(data))

    // Sign the data
    signature, err := rsa.SignPKCS1v15(rand.Reader, privkey, crypto.SHA1, h.Sum(nil))
    if err != nil {
        panic(err)
    }

    // return the results
    return signature
}

func main() {
    if len(os.Args) < 2 {
        fmt.Println("Please give a peer ID as an argument")
        return
    }
    if len(os.Args) < 3 {
        fmt.Println("Please give a voting hash as an argument")
        return
    }
    if len(os.Args) < 4 {
        fmt.Println("Please give a vote hash as an argument")
        return
    }
    if len(os.Args) < 5 {
        fmt.Println("Please give a voter hash as an argument")
        return
    }
    if len(os.Args) < 6 {
        fmt.Println("Please give a name of pub key as an argument")
        return
    }
    if len(os.Args) < 7 {
        fmt.Println("Please give a name of priv key as an argument")
        return
    }

    peerIDofHost := os.Args[1]
    votingHash := os.Args[2]
    voteHash := os.Args[3]
    voterHash := os.Args[4]
    nameOfPubKey := os.Args[5]
    nameOfPrivKey := os.Args[6]

    target, err := peer.IDB58Decode(peerIDofHost)
    if err != nil {
        panic(err)
    }

    // Basic ipfsnode setup
    r, err := fsrepo.Open("~/.ipfsEvoxClient")
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

    for i := 1; i <= 1000; i++ {
        fmt.Println("Connection with host, number: ", i)
        connectionWithHost(votingHash, voteHash, voterHash, nameOfPubKey,
                           nameOfPrivKey, nd, target)
    }
}

func connectionWithHost(votingHash, voteHash, voterHash, nameOfPubKey,
                        nameOfPrivKey string, nd *core.IpfsNode, target peer.ID) {
    bulletin := CreateBulletin(votingHash, voteHash, voterHash, nameOfPubKey)
    signedBulletin := CreateSignedBulletin(bulletin, GetKey(nameOfPrivKey))
    ipfsObjectJSON := CreateIpfsObjectJson(signedBulletin)
 
    // save bulletin to ipfs
    s := httpApi.NewShell(shellUrl)
    hash, err := s.PutObject(encoding, bytes.NewBufferString(ipfsObjectJSON))
    if err != nil {
        panic(err)
    }
    dataForHost := `{"Hash":"` + hash + `"}`

    con, err := corenet.Dial(nd, target, protocolAddress)
    if err != nil {
        fmt.Println(err)
        return
    }
    fmt.Fprintln(con, dataForHost) // send hash of bulletin to the server

    // get data from response
    buf := make([]byte, 256)
    n, err := con.Read(buf)
    if err != nil {
        fmt.Println(err)
        return
    }

    // show data and close script
    response := string(buf[:n])
    if response != "" {
        fmt.Println(response)
        return
    }
}