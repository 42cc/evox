package main

import (
    "encoding/json"
    "reflect"
    "strings"
    "testing"
    "time"

    "../client"
)

const (
    examplesVotingHash = "QmVtU7ths96fMgZ8YSZAbKghyieq7AjxNdcqyVzxTt3qaa"
    examplesVoteHash   = "QmVtU7ths96fMgZ8YSZAbKghyieq7AjxNdcqyVzxTt3qbb"
    examplesVoterHash  = "QmVtU7ths96fMgZ8YSZAbKghyieq7AjxNdcqyVzxTt3qcc"
    privKeyPEM         = `-----BEGIN RSA PRIVATE KEY-----
MIIBOgIBAAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWOhTf8Ph07ZA0KjdbKtfL/
7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/AnsCAwEAAQJAQj9kJrZDuKT6ZyOQZfPD
tobRZ1xjo93/dWU72bF3aHDo4ILMy2Kigy5yhZU0ZGjOuPv5eUOLRe/yxYQf6B5J
AQIhANbhfZ4QJC8dLXAqcsxOXuLgztzbKixUre0gnhiVSd1hAiEAzv+sHJ4PMjKs
Iuf6/nUI9XFgQQRd+NGRovyHRZC18VsCIAX7AKQFjvxAs6MLi2ZkR//IgfljoCjb
snuHDN9iSEwBAiEAmAc1XCtGE+Mdg+GG+T3xn3pubDIN5oHcia0YmKIIzsMCIEy1
fWM5cIJ9bAUExKB6MV8PF+9EjDvXzbSk1/Ycta8z
-----END RSA PRIVATE KEY-----`
    pubKeyPEM         = "test_data/pubkeys/key.pub"
    examplesSignature = `T0EiVgKu8dKN3aSZ503LMvucb67dbkqJ9VHLCzYeF` +
        `3RgTa3u1PDa480PdZlZcmXwy/0PbLkekSg/e/PYNVXJLQ==`
)

func TestCreateIpfsObject(t *testing.T) {
    timeNow := time.Now().Format("2006-02-01T15:04:05.000Z")
    bulletin := main.CreateBulletin(examplesVotingHash,
        examplesVoteHash,
        examplesVoterHash,
        pubKeyPEM)
    signedBulletin := main.CreateSignedBulletin(bulletin, privKeyPEM)
    subStr := `{"Links":null,"Data":"{\` +
        `"bulletin\":{` +
        `\"voting\":\"QmVtU7ths96fMgZ8YSZAbKghyieq7AjxNdcqyVzxTt3qaa\",` +
        `\"vote\":\"QmVtU7ths96fMgZ8YSZAbKghyieq7AjxNdcqyVzxTt3qbb\",` +
        `\"voter\":\"QmVtU7ths96fMgZ8YSZAbKghyieq7AjxNdcqyVzxTt3qcc\",` +
        `\"datetime\":\"` + timeNow + `\",` +
        `\"publickey\":\"-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE` +
        `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT` +
        `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/` +
        `AnsCAwEAAQ==_-----END PUBLIC KEY-----\"}`
    ipfsObject := main.CreateIpfsObject(signedBulletin)
    ipfsObjectBytes, err := json.Marshal(ipfsObject)
    if err != nil {
        panic(err)
    }
    ipfsObjectJSON := string(ipfsObjectBytes)
    if !strings.Contains(ipfsObjectJSON, subStr) {
        t.Errorf("Not found '%v' in '%v'", subStr, ipfsObjectJSON)
    }
}

func TestSignature(t *testing.T) {
    bulletin := main.Bulletin{
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "2016-15-02T21:03:03.983Z",
        `-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE` +
            `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT` +
            `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/` +
            `AnsCAwEAAQ==_-----END PUBLIC KEY-----`,
    }
    expected := `{` +
        `"bulletin":{` +
        `"voting":"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",` +
        `"vote":"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",` +
        `"voter":"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",` +
        `"datetime":"2016-15-02T21:03:03.983Z",` +
        `"publickey":"-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE` +
        `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_` +
        `hTf8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGO` +
        `tDLLA/AnsCAwEAAQ==_-----END PUBLIC KEY-----"` +
        `},` +
        `"signature":"bZu8LPwnQilcSw3cLDsFnf9kDfjxC9OmazDmhk8yESlzlO` +
        `VfgpcyNpWiyP5vIXQm7DcrL6JPIbXBxZ/uuEUtTw=="` +
        `}`
    actual := main.CreateSignedBulletin(bulletin, privKeyPEM)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }

}
