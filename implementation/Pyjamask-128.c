//==============================================================================
// Macros 
//==============================================================================
#define OCB_ENCRYPT 1
#define OCB_DECRYPT 0

/* ------------------------------------------------------------------------- */

#define CRYPTO_KEYBYTES     16
#define CRYPTO_NSECBYTES    0
#define CRYPTO_NPUBBYTES    12
#define CRYPTO_ABYTES       16
#define CRYPTO_NOOVERLAP    1

/* ------------------------------------------------------------------------- */

#define STATE_SIZE_96        3
#define STATE_SIZE_128       4

/* ------------------------------------------------------------------------- */

#define NB_ROUNDS_96        14
#define NB_ROUNDS_128       14
#define NB_ROUNDS_KS        14

/* ------------------------------------------------------------------------- */

#define COL_M0          0xa3861085
#define COL_M1          0x63417021
#define COL_M2          0x692cf280
#define COL_M3          0x48a54813
#define COL_MK          0xb881b9ca

/* ------------------------------------------------------------------------- */

#define COL_INV_M0      0x2037a121
#define COL_INV_M1      0x108ff2a0 
#define COL_INV_M2      0x9054d8c0 
#define COL_INV_M3      0x3354b117

/* ------------------------------------------------------------------------- */

#define KS_CONSTANT_0   0x00000080
#define KS_CONSTANT_1   0x00006a00
#define KS_CONSTANT_2   0x003f0000
#define KS_CONSTANT_3   0x24000000

/* ------------------------------------------------------------------------- */

#define KS_ROT_GAP1      8
#define KS_ROT_GAP2     15
#define KS_ROT_GAP3     18

/* ------------------------------------------------------------------------- */

#define KEYBYTES   CRYPTO_KEYBYTES   // Key length in bytes
#define NONCEBYTES CRYPTO_NPUBBYTES  // Nonce length in bytes
#define TAGBYTES   CRYPTO_ABYTES     // Authentication tag length in bytes

/* ------------------------------------------------------------------------- */

typedef unsigned char block[16]; // Define block as an array of 16 unsigned chars (128-bit blocks)

/* ------------------------------------------------------------------------- */

#define right_rotate(row) \
    row = (row >> 1) | (row << 31);

#define left_rotate(row,n) \
    row = (row >> n) | (row << (32-n));

/* ------------------------------------------------------------------------- */

#include <stdint.h>
#include <string.h>
#include <stdio.h>

//==============================================================================
// Helper
//==============================================================================

void load_state(const uint8_t *plaintext, uint32_t *state, int state_size) {
    int i;

    for (i=0; i<state_size; i++)
    {
        state[i] =                   plaintext[4*i+0];
        state[i] = (state[i] << 8) | plaintext[4*i+1];
        state[i] = (state[i] << 8) | plaintext[4*i+2];
        state[i] = (state[i] << 8) | plaintext[4*i+3];
    }
}

void unload_state(uint8_t *ciphertext, const uint32_t *state, int state_size) {
    int i;

    for (i=0; i<state_size; i++)
    {
        ciphertext [4*i+0] = (uint8_t) (state[i] >> 24);
        ciphertext [4*i+1] = (uint8_t) (state[i] >> 16);
        ciphertext [4*i+2] = (uint8_t) (state[i] >>  8);
        ciphertext [4*i+3] = (uint8_t) (state[i] >>  0);
    }
}

uint32_t mat_mult(uint32_t mat_col, uint32_t vec) {
    int i;
    uint32_t mask, res=0;

    for (i = 31; i>=0; i--)
    {
        mask = -((vec >> i) & 1);
        res ^= mask & mat_col;
        right_rotate(mat_col);
    }

    return res;
}

//==============================================================================
// Key schedule
//==============================================================================

void ks_mix_comlumns(const uint32_t *ks_prev, uint32_t *ks_next) {
    uint32_t tmp;

    tmp = ks_prev[0] ^ ks_prev[1] ^ ks_prev[2] ^ ks_prev[3];

    ks_next[0] = ks_prev[0] ^ tmp;
    ks_next[1] = ks_prev[1] ^ tmp;
    ks_next[2] = ks_prev[2] ^ tmp;
    ks_next[3] = ks_prev[3] ^ tmp;
}

void ks_mix_rotate_rows(uint32_t *ks_state) {
    ks_state[0] = mat_mult(COL_MK, ks_state[0]);
    left_rotate(ks_state[1],KS_ROT_GAP1)
    left_rotate(ks_state[2],KS_ROT_GAP2)
    left_rotate(ks_state[3],KS_ROT_GAP3)
}

void ks_add_constant(uint32_t *ks_state, const uint32_t ctr) {
    ks_state[0] ^= KS_CONSTANT_0 ^ ctr;
    ks_state[1] ^= KS_CONSTANT_1;
    ks_state[2] ^= KS_CONSTANT_2;
    ks_state[3] ^= KS_CONSTANT_3;
}

void key_schedule(const uint8_t *key, uint32_t* round_keys) {
    int r;
    uint32_t *ks_state = round_keys;

    load_state(key, ks_state, 4); 

    for (r=0; r<NB_ROUNDS_KS; r++)
    {
        ks_state += 4;

        ks_mix_comlumns(ks_state-4, ks_state);
        ks_mix_rotate_rows(ks_state);
        ks_add_constant(ks_state,r);

    }    
}

//==============================================================================
// Pyjamask-128 (encryption)
//==============================================================================

void mix_rows_128(uint32_t *state) {
    state[0] = mat_mult(COL_M0, state[0]);
    state[1] = mat_mult(COL_M1, state[1]);
    state[2] = mat_mult(COL_M2, state[2]);
    state[3] = mat_mult(COL_M3, state[3]);
}

void sub_bytes_128(uint32_t *state) {
    state[0] ^= state[3];
    state[3] ^= state[0] & state[1];
    state[0] ^= state[1] & state[2];
    state[1] ^= state[2] & state[3];
    state[2] ^= state[0] & state[3];
    state[2] ^= state[1];
    state[1] ^= state[0];
    state[3] = ~state[3];

    // swap state[2] <-> state[3]
    state[2] ^= state[3];
    state[3] ^= state[2];
    state[2] ^= state[3];
}

void add_round_key_128(uint32_t *state, const uint32_t *round_key, int r) {
    state[0] ^= round_key[4*r+0];
    state[1] ^= round_key[4*r+1];
    state[2] ^= round_key[4*r+2];
    state[3] ^= round_key[4*r+3];
}

void pyjamask_128_enc(const uint8_t *plaintext, const uint8_t *key, uint8_t *ciphertext) {
    int r;
    uint32_t state[STATE_SIZE_128];
    uint32_t round_keys[4*(NB_ROUNDS_KS+1)];

    key_schedule(key, round_keys);
    load_state(plaintext, state, STATE_SIZE_128);


    for (r=0; r<NB_ROUNDS_128; r++)
    {
        add_round_key_128(state, round_keys, r);
        sub_bytes_128(state);
        mix_rows_128(state);
    }

    add_round_key_128(state, round_keys, NB_ROUNDS_128);
    
    unload_state(ciphertext, state, STATE_SIZE_128);
}

//==============================================================================
// Pyjamask-128 (decryption)
//==============================================================================

void inv_mix_rows_128(uint32_t *state) {
    state[0] = mat_mult(COL_INV_M0, state[0]);
    state[1] = mat_mult(COL_INV_M1, state[1]);
    state[2] = mat_mult(COL_INV_M2, state[2]);
    state[3] = mat_mult(COL_INV_M3, state[3]);
}

void inv_sub_bytes_128(uint32_t *state) {
    // swap state[2] <-> state[3]
    state[2] ^= state[3];
    state[3] ^= state[2];
    state[2] ^= state[3];

    state[3] = ~state[3];
    state[1] ^= state[0];
    state[2] ^= state[1];
    state[2] ^= state[3] & state[0];
    state[1] ^= state[2] & state[3];
    state[0] ^= state[1] & state[2];
    state[3] ^= state[0] & state[1];
    state[0] ^= state[3];
}

void pyjamask_128_dec(const uint8_t *ciphertext, const uint8_t *key, uint8_t *plaintext) {
    int r;
    uint32_t state[STATE_SIZE_128];
    uint32_t round_keys[4*(NB_ROUNDS_KS+1)];

    key_schedule(key, round_keys);
    load_state(ciphertext, state, STATE_SIZE_128);

    add_round_key_128(state, round_keys, NB_ROUNDS_128);
    
    for (r=NB_ROUNDS_128-1; r>=0; r--)
    {
        inv_mix_rows_128(state);
        inv_sub_bytes_128(state);
        add_round_key_128(state, round_keys, r);
    }

    unload_state(plaintext, state, STATE_SIZE_128);
}

//==============================================================================
// Helper
//==============================================================================

static void xor_block(block d, block s1, block s2) {
    unsigned i;
    for (i = 0; i < 16; i++)
        d[i] = s1[i] ^ s2[i];  // XOR each byte of the blocks
}

static void double_block(block d, block s) {
    unsigned i;
    unsigned char tmp = s[0];
    for (i = 0; i < 15; i++)
        d[i] = (s[i] << 1) | (s[i + 1] >> 7);  // Left shift each byte, carry bits to the next byte
    d[15] = (s[15] << 1) ^ ((tmp >> 7) * 135);  // Handle the last byte with an XOR operation if needed
}

static void calc_L_i(block l, block ldollar, unsigned i) {
    double_block(l, ldollar);  // L_0 -> L_1
    for (; (i & 1) == 0; i >>= 1)  // For every trailing zero in i, double the value of L
        double_block(l, l);
}

/* ------------------------------------------------------------------------- */

static void hash(block result, unsigned char *k,
                 unsigned char *a, unsigned abytes) {
    block lstar, ldollar, offset, sum, tmp;
    unsigned i;

    // Key-dependent variables

    // L_* = ENCIPHER(K, zeros(128))
    memset(tmp, 0, 16);  // Set the temporary block to all zeros
    pyjamask_128_enc(tmp, k, lstar);  // Encrypt the all-zero block with the key to get Lstar
    double_block(ldollar, lstar);  // L_$ = double(L_*)

    // Process any whole blocks of associated data
    memset(sum, 0, 16);  // Initialize sum as a zero block
    memset(offset, 0, 16);  // Initialize offset as a zero block

    for (i = 1; i <= abytes / 16; i++, a = a + 16) {
        calc_L_i(tmp, ldollar, i);  // Calculate L_i for the current block index
        xor_block(offset, offset, tmp);  // Update the offset by XORing the current L_i with the previous offset
        xor_block(tmp, offset, a);  // XOR the current associated data block with the offset
        pyjamask_128_enc(tmp, k, tmp);  // Encrypt the result using the key
        xor_block(sum, sum, tmp);  // XOR the encrypted result into the sum
    }

    // Process the final partial block of associated data
    abytes = abytes % 16;  // Handle any remaining bytes in the final block
    if (abytes > 0) {
        xor_block(offset, offset, lstar);  // XOR the final offset with L_*
        memset(tmp, 0, 16);  // Clear the temporary block
        memcpy(tmp, a, abytes);  // Copy the final partial block
        tmp[abytes] = 0x80;  // Set the 128th bit to indicate end of the block
        xor_block(tmp, offset, tmp);  // XOR with the offset
        pyjamask_128_enc(tmp, k, tmp);  // Encrypt with the key
        xor_block(sum, tmp, sum);  // XOR the result into the sum
    }

    memcpy(result, sum, 16);  // Copy the final hash into the result
}

/* ------------------------------------------------------------------------- */

static int ocb_crypt(unsigned char *out, unsigned char *k, unsigned char *n,
                     unsigned char *a, unsigned abytes,
                     unsigned char *in, unsigned inbytes, int encrypting) {
    block lstar, ldollar, sum, offset, ktop, pad, nonce, tag, tmp, ad_hash;
    unsigned char stretch[24];
    unsigned bottom, byteshift, bitshift, i;

    // Setup AES and strip ciphertext of its tag
    if (!encrypting) {
        if (inbytes < TAGBYTES) return -1;  // If ciphertext is smaller than the tag, it's invalid
        inbytes -= TAGBYTES;  // Remove the tag from ciphertext size
    }

    // Key-dependent variables

    memset(tmp, 0, 16);  // Initialize temporary block
    pyjamask_128_enc(tmp, k, lstar);  // Encrypt the all-zero block with the key
    double_block(ldollar, lstar);  // L_$ = double(L_*)

    // Nonce-dependent and per-encryption variables

    memset(nonce, 0, 16);  // Initialize nonce block to all zeros
    memcpy(&nonce[16 - NONCEBYTES], n, NONCEBYTES);  // Copy the nonce into the last part of the block
    nonce[0] = (unsigned char)(((TAGBYTES * 8) % 128) << 1);  // Set the first bit of nonce
    nonce[16 - NONCEBYTES - 1] |= 0x01;  // Set the last byte to indicate nonce

    bottom = nonce[15] & 0x3F;  // Get the bottom 6 bits of the nonce
    nonce[15] &= 0xC0;  // Mask the top 2 bits of the nonce

    pyjamask_128_enc(nonce, k, ktop);  // Encrypt nonce to get ktop
    memcpy(stretch, ktop, 16);  // Copy ktop into stretch
    memcpy(tmp, &ktop[1], 8);  // Copy part of ktop for XOR operation
    xor_block(tmp, tmp, ktop);  // XOR the two parts to create a stretch
    memcpy(&stretch[16], tmp, 8);  // Store the XOR result in the second half of stretch

    // Offset calculation
    byteshift = bottom / 8;
    bitshift = bottom % 8;
    if (bitshift != 0) {
        for (i = 0; i < 16; i++)
            offset[i] = (stretch[i + byteshift] << bitshift) | (stretch[i + byteshift + 1] >> (8 - bitshift));
    } else {
        for (i = 0; i < 16; i++)
            offset[i] = stretch[i + byteshift];  // No bit shift, just copy
    }

    memset(sum, 0, 16);  // Initialize sum as a zero block

    // Hash associated data
    hash(ad_hash, k, a, abytes);  // Hash the associated data


    // Process any whole blocks of data
    for (i = 1; i <= inbytes / 16; i++, in = in + 16, out = out + 16) {
        calc_L_i(tmp, ldollar, i);  // Calculate L_i for the current block index
        xor_block(offset, offset, tmp);  // Update offset with L_i

        xor_block(tmp, offset, in);  // XOR the current block of input with the offset
        if (encrypting) {
            xor_block(sum, in, sum);  // Update checksum for encryption
            pyjamask_128_enc(tmp, k, tmp);  // Encrypt the block
            xor_block(out, offset, tmp);  // XOR encrypted block into the output
        } else {
            pyjamask_128_dec(tmp, k, tmp);  // Decrypt the block for decryption
            xor_block(out, offset, tmp);  // XOR decrypted block into the output
            xor_block(sum, out, sum);  // Update checksum for decryption
        }
    }

    // Process final partial block and compute tag
    inbytes = inbytes % 16;  // Handle any remaining bytes
    if (inbytes > 0) {
        xor_block(offset, offset, lstar);  // XOR the final offset with L_*
        pyjamask_128_enc(offset, k, pad);  // Encrypt the final offset

        if (encrypting) {
            memset(tmp, 0, 16);  // Clear temporary block
            memcpy(tmp, in, inbytes);  // Copy remaining input
            tmp[inbytes] = 0x80;  // Set the padding byte
            xor_block(sum, tmp, sum);  // Update checksum
            xor_block(pad, tmp, pad);  // XOR pad with the remaining data
            memcpy(out, pad, inbytes);  // Write the result to output
            out = out + inbytes;
        } else {
            memcpy(tmp, pad, 16);  // Copy pad to temp block
            memcpy(tmp, in, inbytes);  // Copy remaining input to temp block
            xor_block(tmp, pad, tmp);  // XOR with pad
            tmp[inbytes] = 0x80;  // Add padding byte
            memcpy(out, tmp, inbytes);  // Write output to the buffer
            xor_block(sum, tmp, sum);  // Update checksum for decryption
            in = in + inbytes;
        }
    }

    // Calculate final tag
    xor_block(tmp, sum, offset);  // XOR sum with offset
    xor_block(tmp, tmp, ldollar);  // XOR with L_$
    pyjamask_128_enc(tmp, k, tag);  // Encrypt the result
    xor_block(tag, ad_hash, tag);  // XOR with associated data hash

    if (encrypting) {
        memcpy(out, tag, TAGBYTES);  // Output the tag if encrypting
        return 0;
    } else {
        return (memcmp(in, tag, TAGBYTES) ? -1 : 0);  // Check for validity of the tag in decryption
    }
}

/* ------------------------------------------------------------------------- */

void ocb_encrypt(unsigned char *c, unsigned char *k, unsigned char *n,
                 unsigned char *a, unsigned abytes,
                 unsigned char *p, unsigned pbytes) {
    ocb_crypt(c, k, n, a, abytes, p, pbytes, OCB_ENCRYPT);  
}

/* ------------------------------------------------------------------------- */

int ocb_decrypt(unsigned char *p, unsigned long long *mlen,
                unsigned char *nsec,
                const unsigned char *c,unsigned long long clen,
                const unsigned char *ad,unsigned long long adlen,
                const unsigned char *npub,
                const unsigned char *k) {
    return ocb_crypt(p, (unsigned char *)k, (unsigned char *)npub,
                     (unsigned char *)ad, adlen, (unsigned char *)c, clen, OCB_DECRYPT);
}

/* ------------------------------------------------------------------------- */

int crypto_aead_encrypt(unsigned char *c,unsigned long long *clen,
                        const unsigned char *m,unsigned long long mlen,
                        const unsigned char *ad,unsigned long long adlen,
                        const unsigned char *nsec,
                        const unsigned char *npub,
                        const unsigned char *k) {
    (void)(nsec);  // Unused argument for AEAD encryption
    *clen = mlen + TAGBYTES;  // Output length is plaintext size + tag
    ocb_crypt(c, (unsigned char *)k, (unsigned char *)npub, (unsigned char *)ad,
            adlen, (unsigned char *)m, mlen, OCB_ENCRYPT);
    return 0;
}

/* ------------------------------------------------------------------------- */

int crypto_aead_decrypt(unsigned char *m,unsigned long long *mlen,
                        unsigned char *nsec,
                        const unsigned char *c,unsigned long long clen,
                        const unsigned char *ad,unsigned long long adlen,
                        const unsigned char *npub,
                        const unsigned char *k) {
    (void)(nsec);  // Unused argument for AEAD decryption
    *mlen = clen - TAGBYTES;  // Output length is ciphertext size minus the tag
    return ocb_crypt(m, (unsigned char *)k, (unsigned char *)npub,
            (unsigned char *)ad, adlen, (unsigned char *)c, clen, OCB_DECRYPT);
}

//==============================================================================
// Main
//==============================================================================

int main() {
    unsigned char key[KEYBYTES] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0F };  // Example key
    unsigned char nonce[NONCEBYTES] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B };  // Example nonce
    unsigned char plaintext[] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0F };  // Example plaintext
    unsigned char ciphertext[sizeof(plaintext) + TAGBYTES];  
    unsigned char decrypted[sizeof(plaintext)];  
    unsigned long long clen, mlen;
    
    // Encrypt the plaintext
    crypto_aead_encrypt(ciphertext, &clen, plaintext, sizeof(plaintext), NULL, 0, NULL, nonce, key);
    
    // Decrypt the ciphertext
    crypto_aead_decrypt(decrypted, &mlen, NULL, ciphertext, clen, NULL, 0, nonce, key);
    
    // Print plaintext in hex format
    printf("%-20s", "Plaintext : ");
    for (int i = 0; i < sizeof(plaintext); i++) {
        printf("%02X ", plaintext[i]);
    }
    printf("\n");
    
    // Print key in hex format
    printf("%-20s", "Key : ");
    for (int i = 0; i < KEYBYTES; i++) {
        printf("%02X ", key[i]);
    }
    printf("\n");

    // Print nonce in hex format
    printf("%-20s", "Nonce : ");
    for (int i = 0; i < NONCEBYTES; i++) {
        printf("%02X ", nonce[i]);
    }
    printf("\n");

    // Print data in hex format (e.g., plaintext or ciphertext)
    printf("%-20s", "Data :");
    for (unsigned long long i = 0; i < sizeof(plaintext); i++) {
        printf("%02X ", plaintext[i]);
    }
    printf("\n");

    // Print ciphertext in hex format
    printf("%-20s", "Ciphertext : ");
    for (unsigned long long i = 0; i < sizeof(plaintext); i++) {
        printf("%02X ", ciphertext[i]);
    }
    printf("\n");

    // Print tag in hex format
    printf("%-20s", "Tag : ");
    for (unsigned long long i = clen - TAGBYTES; i < clen; i++) {
        printf("%02X ", ciphertext[i]);
    }
    printf("\n");

    // Print decrypted message
    printf("%-20s", "Decrypted message : ");
    for (unsigned long long i = 0; i < mlen; i++) {
        printf("%02X ", decrypted[i]);
    }
    printf("\n");

    return 0;
}