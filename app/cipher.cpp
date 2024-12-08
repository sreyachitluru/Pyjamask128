#include <bits/stdc++.h>
using namespace std;



//==============================================================================
/* PARAMETERS */
//==============================================================================

const uint8_t S4[16] = {0x2, 0xd, 0x3, 0x9, 0x7, 0xb, 0xa, 0x6, 0xe, 0x0, 0xf, 0x4, 0x8, 0x5, 0x1, 0xc};
const uint8_t invS4[16] = {0x9, 0xe, 0x0, 0x2, 0xb, 0xd, 0x7, 0x4, 0xc, 0x3, 0x6, 0x5, 0xf, 0x1, 0x8, 0xa};

const uint32_t M0 = 0xa3861085;
const uint32_t M1 = 0x63417021;
const uint32_t M2 = 0x692cf280;
const uint32_t M3 = 0x48a54813;

const uint32_t MK = 0xb881b9ca;

const uint32_t invM0 = 0x2037a121;
const uint32_t invM1 = 0x108ff2a0; 
const uint32_t invM2 = 0x9054d8c0; 
const uint32_t invM3 = 0x3354b117;

const uint32_t keyScheduleC0 = 0x00000080;
const uint32_t keyScheduleC1 = 0x00006a00;
const uint32_t keyScheduleC2 = 0x003f0000;
const uint32_t keyScheduleC3 = 0x24000000;



//==============================================================================
/* HELPER FUNCTIONS */
//==============================================================================

// checked - works correctly
string dbl(const string& x) {
    unsigned char d[16];
    unsigned char tmp = x[0];

    for (unsigned i = 0; i < 15; i++) {
        d[i] = (x[i] << 1) | (x[i + 1] >> 7);
    }

    d[15] = (x[15] << 1) ^ ((tmp >> 7) * 135); 

    string result(d, d + 16);
    return result;
}

// checked - works correctly
int ntz(uint32_t x) {
    if (x == 0) return 32;
    int count = 0;
    while ((x & 1) == 0) {
        count++;
        x >>= 1;
    }
    return count;
}

// checked - works correctly
void right_rotate(uint32_t &row, int n = 1) {
    row = (row >> n) | (row << (32 - n));
}

// checked - works correctly
void left_rotate(uint32_t &row, int n) {
    row = (row << n) | (row >> (32 - n));
}

// checked - works correctly
string xor_block(string block1, string block2) {
    string resultStr (16, '\0');
    for (int i = 0; i < 16; i++) {
        resultStr[i] = block1[i] ^ block2[i];
    }

    return resultStr;
}

uint32_t mat_mult(uint32_t mat_col, uint32_t vec) {
    uint32_t mask, res=0;

    for (int i = 31; i>=0; i--) {
        mask = -((vec >> i) & 1);
        res ^= mask & mat_col;
        right_rotate(mat_col);
    }

    return res;
}

// checked - works correctly
vector<uint32_t> Load(string plaintext) {
    vector<uint32_t> state(4, 0);
    for (int i = 0; i < 4; i++) {
        state[i] = (uint8_t) plaintext[4 * i + 0];
        state[i] = (state[i] << 8) | (uint8_t) plaintext[4 * i + 1];
        state[i] = (state[i] << 8) | (uint8_t) plaintext[4 * i + 2];
        state[i] = (state[i] << 8) | (uint8_t) plaintext[4 * i + 3];
    }
    return state;
}

// checked - works correctly
string Unload(vector<uint32_t> state) {
    string ciphertext(16, '\0');
    for (int i = 0; i < 4; i++) {
        ciphertext[4 * i + 0] = (uint8_t) (state[i] >> 24);
        ciphertext[4 * i + 1] = (uint8_t) (state[i] >> 16);
        ciphertext[4 * i + 2] = (uint8_t) (state[i] >> 8);
        ciphertext[4 * i + 3] = (uint8_t) (state[i] >> 0);
    }
    return ciphertext;
}



//==============================================================================
/* KEY SCHEDULING */
//==============================================================================

// checked - works correctly
void MixComlumns(vector <uint32_t> &previousState, vector <uint32_t> &currentState) {
    uint32_t tmp = previousState[0] ^ previousState[1] ^ previousState[2] ^ previousState[3];
    currentState[0] = previousState[0] ^ tmp;
    currentState[1] = previousState[1] ^ tmp;
    currentState[2] = previousState[2] ^ tmp;
    currentState[3] = previousState[3] ^ tmp;
}

// checked - works correctly
void MixAndRotateRows(vector <uint32_t> &currentState) {
    currentState[0] = mat_mult(MK, currentState[0]);
    left_rotate(currentState[1], 8);
    left_rotate(currentState[2], 15);
    left_rotate(currentState[3], 18);
}

// checked - works correctly
void AddConstant(vector <uint32_t> &currentState, const uint32_t ctr) {
    currentState[0] ^= keyScheduleC0 ^ ctr;
    currentState[1] ^= keyScheduleC1;
    currentState[2] ^= keyScheduleC2;
    currentState[3] ^= keyScheduleC3;
}

vector<vector<uint32_t>> KeySchedule(string key) {
    vector<vector<uint32_t>> roundKeys;
    vector <uint32_t> previousState; 
    vector <uint32_t> currentState = Load(key); 
    roundKeys.push_back(currentState);

    for (int r=0; r<14; r++) {
        previousState = currentState;
        MixComlumns(previousState, currentState);
        MixAndRotateRows(currentState);
        AddConstant(currentState, r);
        roundKeys.push_back(currentState);
    }    

    return roundKeys;
}



//==============================================================================
/* ENCRYPTION */
//==============================================================================

// checked - works correctly
void AddRoundKey(vector<uint32_t>& state, vector<vector<uint32_t>>& roundKeys, int r) {
    state[0] ^= roundKeys[r][0];
    state[1] ^= roundKeys[r][1];
    state[2] ^= roundKeys[r][2];
    state[3] ^= roundKeys[r][3];
}

// checked - works correctly
void SubBytes(vector<uint32_t> &state) {
    for (int col = 1; col <= 32; col++) {
        uint8_t sboxIn = 0;

        for (int row = 0; row < 4; row++) {
            uint8_t bit = (state[row] >> (32 - col)) & 1; 
            sboxIn |= (bit << (4-row-1)); 
        }
        
        uint8_t sboxOut = S4[sboxIn];
        for (int row = 0; row < 4; row++) {
            state[row] = (state[row] & ~(1 << (32 - col))) | (((sboxOut >> (4 - row - 1)) & 1) << (32 - col));
        }
    }
}

// checked - works correctly
void MixRows(vector<uint32_t> &state) {
    state[0] = mat_mult(M0, state[0]);
    state[1] = mat_mult(M1, state[1]);
    state[2] = mat_mult(M2, state[2]);
    state[3] = mat_mult(M3, state[3]);
}

string encryption_util (string plaintext, vector<vector<uint32_t>> &roundKeys) {
    vector<uint32_t> state = Load(plaintext);

    for (int i = 1; i < 14; ++i) {
        AddRoundKey(state, roundKeys, i);
        SubBytes(state);
        MixRows(state);
    }

    AddRoundKey(state, roundKeys, 14);

    return Unload(state);
}

vector <string> initialisation(string text, vector<vector<uint32_t>> &roundKeys) {
    int I = text.length()/16; 
    
    string zeroBlock(16, '\0');

    vector <string> allLi;
    string L_star = encryption_util(zeroBlock, roundKeys);
    string L_dollar = dbl(L_star);

    allLi.push_back(L_star);
    allLi.push_back(L_dollar);
    for (int i=0; i<=I; i++) {
        allLi.push_back(dbl(allLi[i+1]));
    }

    return allLi;
}

string hashAD(string associatedData, vector<vector<uint32_t>> &roundKeys) {
    string authenticationTag = "";
    string currentOutput (16, '\0');
    string currentOffset (16, '\0');

    vector <string> allLi = initialisation(associatedData, roundKeys);
    string L_star = allLi[0]; 
    string L_dollar = allLi[1];
    
    int fullBlocks = associatedData.length()/16;
    for (int i=1; i <= fullBlocks; i++) { 
        string currentAssociatedData = string(associatedData.begin()+(i-1)*16, associatedData.begin()+i*16);
    
        int trailingZeroes = ntz(i-1);
        string currentLi = allLi[trailingZeroes+2]; 
        currentOffset = xor_block(currentOffset, currentLi);
        
        string inputEncrypt = xor_block(currentAssociatedData, currentOffset);
        string outputEncrypt = encryption_util(inputEncrypt, roundKeys);

        currentOutput = xor_block(currentOutput, outputEncrypt);
        authenticationTag = currentOutput;
    }

    if (associatedData.length()%16) {
        string currentAssociatedData = string(associatedData.begin()+fullBlocks*16, associatedData.end()); 
        currentAssociatedData.resize(16, 0x00); 
        currentAssociatedData[currentAssociatedData.size() - 16 + (associatedData.size() % 16)] = 0x80;
    
        string currentLi = L_star;
        string Offset_star = xor_block(currentOffset, currentLi);
        
        string inputEncrypt = xor_block(currentAssociatedData, Offset_star);
        string outputEncrypt = encryption_util(inputEncrypt, roundKeys);

        currentOutput = xor_block(currentOutput, outputEncrypt);
        authenticationTag = currentOutput;
    }

    return authenticationTag;
}

vector <string> encryption (string plaintext, string associatedData, string nonce, string key) {
    vector<vector<uint32_t>> roundKeys = KeySchedule(key);
    
    vector <string> allLi = initialisation(plaintext, roundKeys);
    string L_star = allLi[0]; 
    string L_dollar = allLi[1];
    
    string hashAuth = hashAD(associatedData, roundKeys);
    string ciphertext = "";

    string currentOffset(16, '\0');
    string currentSum(16, '\0');

    nonce.resize(16, 0x00);
    nonce[nonce.size() - 16 + nonce.size()] = 0x80;

    uint8_t bottom = nonce[15] & 0x3F; 
    string Ktop = encryption_util(nonce.substr(0, 16), roundKeys); 
    string Stretch = Ktop + xor_block(Ktop.substr(0, 8), Ktop.substr(8, 8));
    currentOffset = Stretch.substr(1 + bottom, 16);

    int fullBlocks = plaintext.length()/16;
    for (int i=1; i <= fullBlocks; i++) { 
        string currentPlaintext = string(plaintext.begin() + (i - 1) * 16, plaintext.begin() + i * 16); 
        
        int trailingZeroes = ntz(i-1);
        string currentLi = allLi[trailingZeroes+2]; 
        currentOffset = xor_block(currentOffset, currentLi);
        
        string inputEncrypt = xor_block(currentPlaintext, currentOffset);
        string outputEncrypt = encryption_util(inputEncrypt, roundKeys);

        string currentCiphertext = xor_block(outputEncrypt, currentOffset);

        ciphertext += currentCiphertext;

        currentSum = xor_block(currentSum, currentPlaintext);
    }

    if (plaintext.size() % 16 != 0) {
        string M_star = string(plaintext.begin() + fullBlocks * 16, plaintext.end());
        M_star.resize(16, 0x00);
        M_star[M_star.size() - 16 + (plaintext.size() % 16)] = 0x80;

        string Offset_star = xor_block(currentOffset, L_star);
        string Pad = encryption_util(Offset_star, roundKeys);
        string C_star = xor_block(M_star, Pad.substr(0, M_star.size()));
        ciphertext += C_star;

        currentSum = xor_block(currentSum, M_star);
        currentSum[M_star.size() - 16 + (plaintext.size() % 16)] = 0x80;
    } 
    
    currentOffset = xor_block(currentOffset, L_dollar);
    string tag = xor_block(
        encryption_util(xor_block(currentSum, currentOffset), roundKeys),
        hashAuth
    );
    
    vector <string> ans = {tag, ciphertext};
    return ans;
}



//==============================================================================
/* DECRYPTION */
//==============================================================================

// checked - works correctly
void invMixRows(vector<uint32_t>& state) {
    state[0] = mat_mult(invM0, state[0]);
    state[1] = mat_mult(invM1, state[1]);
    state[2] = mat_mult(invM2, state[2]);
    state[3] = mat_mult(invM3, state[3]);
}

// checked - works correctly
void invSubBytes(vector<uint32_t>& state) {
    for (int col = 1; col <= 32; col++) {
        uint8_t invsboxIn = 0;

        for (int row = 0; row < 4; row++) {
            uint8_t bit = (state[row] >> (32 - col)) & 1; 
            invsboxIn |= (bit << (4-row-1)); 
        }
        
        uint8_t invsboxOut = invS4[invsboxIn];
        for (int row = 0; row < 4; row++) {
            state[row] = (state[row] & ~(1 << (32 - col))) | (((invsboxOut >> (4 - row - 1)) & 1) << (32 - col));
        }
    }
}

// checked - works correctly
void invAddRoundKey(vector<uint32_t>& state, vector<vector<uint32_t>>& roundKeys, int r) {
    state[0] ^= roundKeys[r][0];
    state[1] ^= roundKeys[r][1];
    state[2] ^= roundKeys[r][2];
    state[3] ^= roundKeys[r][3];
}

string decryption_util (string ciphertext, vector<vector<uint32_t>>& roundKeys) {
    vector<uint32_t> state = Load(ciphertext);

    for (int i = 1; i < 14; ++i) {
        invMixRows(state);
        invSubBytes(state);
        invAddRoundKey(state, roundKeys, i);
    }

    invAddRoundKey(state, roundKeys, 14);

    return Unload(state);
}

string decryption(string ciphertext, string associatedData, string nonce, string key, string tag) {
    vector<vector<uint32_t>> roundKeys = KeySchedule(key);
    
    vector<string> allLi = initialisation(ciphertext, roundKeys);
    string L_star = allLi[0]; 
    string L_dollar = allLi[1]; 
    
    string currentOffset(16, '\0');
    string currentSum(16, '\0');
    
    string plaintext = "";

    nonce.resize(16, 0x00);
    nonce[nonce.size() - 16 + nonce.size()] = 0x80;

    uint8_t bottom = nonce[15] & 0x3F;
    string Ktop = decryption_util(nonce.substr(0, 16), roundKeys);
    string Stretch = Ktop + xor_block(Ktop.substr(0, 8), Ktop.substr(8, 8));
    currentOffset = Stretch.substr(1 + bottom, 16);

    int fullBlocks = ciphertext.size() / 16;
    for (int i = 1; i <= fullBlocks; i++) {
        string currentLi = allLi[ntz(i)];
        currentOffset = xor_block(currentOffset, currentLi);

        string currentCiphertext = string(ciphertext.begin() + (i - 1) * 16, ciphertext.begin() + i * 16);
        string inputDecrypt = xor_block(currentCiphertext, currentOffset);
        string outputDecrypt = decryption_util(inputDecrypt, roundKeys); 
        
        string currentPlaintext = xor_block(outputDecrypt, currentOffset);
        plaintext += currentPlaintext;

        currentSum = xor_block(currentSum, currentPlaintext);
    }

    if (ciphertext.size() % 16 != 0) {
        string C_star = string(ciphertext.begin() + fullBlocks * 16, ciphertext.end());
        string Offset_star = xor_block(currentOffset, L_star);
        string Pad = decryption_util(Offset_star, roundKeys);
        string M_star = xor_block(C_star, Pad.substr(0, C_star.size()));

        plaintext += M_star;

        currentSum = xor_block(currentSum, M_star);
        currentSum[M_star.size() - 16 + (ciphertext.size() % 16)] = 0x80;

        currentOffset = xor_block(Offset_star, L_dollar);
        string tag0 = xor_block(
            decryption_util(xor_block(currentSum, currentOffset), roundKeys),
            hashAD(associatedData, roundKeys)
        );

        if (tag0 != tag) {
            return "⊥"; 
        }
    } else {
        currentOffset = xor_block(currentOffset, L_dollar);
        string tag0 = xor_block(
            decryption_util(xor_block(currentSum, currentOffset), roundKeys),
            hashAD(associatedData, roundKeys)
        );

        if (tag0 != tag) {
            return "⊥"; 
        }
    }

    return plaintext;
}



//==============================================================================
/* MAIN FUNCTION */
//==============================================================================

void printHex(const string &s) {
    for (unsigned char c : s) {
        cout << hex << setw(2) << setfill('0') << (int)c << " ";
    }
    cout << endl;
}

int main() {
    string key = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"; 
    string nonce = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b";
    string associatedData = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f";;
    string plaintext = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f";
    
    vector <string> encryptionOutput;
    string authenticationTag;
    string ciphertext;
    encryptionOutput = encryption(plaintext, associatedData, nonce, key);    
    authenticationTag = encryptionOutput[0];
    ciphertext = encryptionOutput[1];

    string decryptionOutput;
    decryptionOutput = decryption(ciphertext, associatedData, nonce, key, authenticationTag);

    cout << "Key: ";
    printHex(key);
    cout << "Nonce: ";
    printHex(nonce);
    cout << "Associated Data: ";
    printHex(associatedData);
    cout << "Plaintext: ";
    printHex(plaintext);

    cout << "Authentication Tag: ";
    printHex(authenticationTag);
    cout << "Ciphertext Tag: ";
    printHex(ciphertext);

    cout << "Decryption Output (Error/Plaintext): ";
    printHex(decryptionOutput);

    return 0;
}