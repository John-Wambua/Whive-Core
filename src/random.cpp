// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2018 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <random.h>

#include <crypto/sha512.h>
#include <support/cleanse.h>
#ifdef WIN32
#include <compat.h> // for Windows API
#include <wincrypt.h>
#endif
#include <logging.h>  // for LogPrint()
#include <utiltime.h> // for GetTime()

#include <stdlib.h>
#include <chrono>
#include <thread>

#ifndef WIN32
#include <fcntl.h>
#include <sys/time.h>
#endif

#ifdef HAVE_SYS_GETRANDOM
#include <sys/syscall.h>
#include <linux/random.h>
#endif
#if defined(HAVE_GETENTROPY) || (defined(HAVE_GETENTROPY_RAND) && defined(MAC_OSX))
#include <unistd.h>
#endif
#if defined(HAVE_GETENTROPY_RAND) && defined(MAC_OSX)
#include <sys/random.h>
#endif
#ifdef HAVE_SYSCTL_ARND
#include <utilstrencodings.h> // for ARRAYLEN
#include <sys/sysctl.h>
#endif

#include <mutex>

#if defined(__x86_64__) || defined(__amd64__) || defined(__i386__)
#include <cpuid.h>
#endif

#include <openssl/err.h>
#include <openssl/rand.h>

[[noreturn]] static void RandFailure()
{
    LogPrintf("Failed to read randomness, aborting\n");
    std::abort();
}

static inline int64_t GetPerformanceCounter()
{
    // Read the hardware time stamp counter when available.
    // See https://en.wikipedia.org/wiki/Time_Stamp_Counter for more information.
#if defined(_MSC_VER) && (defined(_M_IX86) || defined(_M_X64))
    return __rdtsc();
#elif !defined(_MSC_VER) && defined(__i386__)
    uint64_t r = 0;
    __asm__ volatile ("rdtsc" : "=A"(r)); // Constrain the r variable to the eax:edx pair.
    return r;
#elif !defined(_MSC_VER) && (defined(__x86_64__) || defined(__amd64__))
    uint64_t r1 = 0, r2 = 0;
    __asm__ volatile ("rdtsc" : "=a"(r1), "=d"(r2)); // Constrain r1 to rax and r2 to rdx.
    return (r2 << 32) | r1;
#else
    // Fall back to using C++11 clock (usually microsecond or nanosecond precision)
    return std::chrono::high_resolution_clock::now().time_since_epoch().count();
#endif
}


#if defined(__x86_64__) || defined(__amd64__) || defined(__i386__)
<<<<<<< HEAD
static std::atomic<bool> hwrand_initialized{false};
static bool rdrand_supported = false;
static constexpr uint32_t CPUID_F1_ECX_RDRAND = 0x40000000;
static void RDRandInit()
{
    uint32_t eax, ebx, ecx, edx;
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx) && (ecx & CPUID_F1_ECX_RDRAND)) {
=======
static bool g_rdrand_supported = false;
static bool g_rdseed_supported = false;
static constexpr uint32_t CPUID_F1_ECX_RDRAND = 0x40000000;
static constexpr uint32_t CPUID_F7_EBX_RDSEED = 0x00040000;
#ifdef bit_RDRND
static_assert(CPUID_F1_ECX_RDRAND == bit_RDRND, "Unexpected value for bit_RDRND");
#endif
#ifdef bit_RDSEED
static_assert(CPUID_F7_EBX_RDSEED == bit_RDSEED, "Unexpected value for bit_RDSEED");
#endif
static void inline GetCPUID(uint32_t leaf, uint32_t subleaf, uint32_t& a, uint32_t& b, uint32_t& c, uint32_t& d)
{
    // We can't use __get_cpuid as it doesn't support subleafs.
#ifdef __GNUC__
    __cpuid_count(leaf, subleaf, a, b, c, d);
#else
    __asm__ ("cpuid" : "=a"(a), "=b"(b), "=c"(c), "=d"(d) : "0"(leaf), "2"(subleaf));
#endif
}

static void InitHardwareRand()
{
    uint32_t eax, ebx, ecx, edx;
    GetCPUID(1, 0, eax, ebx, ecx, edx);
    if (ecx & CPUID_F1_ECX_RDRAND) {
        g_rdrand_supported = true;
    }
    GetCPUID(7, 0, eax, ebx, ecx, edx);
    if (ebx & CPUID_F7_EBX_RDSEED) {
        g_rdseed_supported = true;
    }
}

static void ReportHardwareRand()
{
    // This must be done in a separate function, as HWRandInit() may be indirectly called
    // from global constructors, before logging is initialized.
    if (g_rdseed_supported) {
        LogPrintf("Using RdSeed as additional entropy source\n");
    }
    if (g_rdrand_supported) {
>>>>>>> upstream/0.18
        LogPrintf("Using RdRand as an additional entropy source\n");
        rdrand_supported = true;
    }
    hwrand_initialized.store(true);
}
<<<<<<< HEAD
=======

/** Read 64 bits of entropy using rdrand.
 *
 * Must only be called when RdRand is supported.
 */
static uint64_t GetRdRand() noexcept
{
    // RdRand may very rarely fail. Invoke it up to 10 times in a loop to reduce this risk.
#ifdef __i386__
    uint8_t ok;
    uint32_t r1, r2;
    for (int i = 0; i < 10; ++i) {
        __asm__ volatile (".byte 0x0f, 0xc7, 0xf0; setc %1" : "=a"(r1), "=q"(ok) :: "cc"); // rdrand %eax
        if (ok) break;
    }
    for (int i = 0; i < 10; ++i) {
        __asm__ volatile (".byte 0x0f, 0xc7, 0xf0; setc %1" : "=a"(r2), "=q"(ok) :: "cc"); // rdrand %eax
        if (ok) break;
    }
    return (((uint64_t)r2) << 32) | r1;
#elif defined(__x86_64__) || defined(__amd64__)
    uint8_t ok;
    uint64_t r1;
    for (int i = 0; i < 10; ++i) {
        __asm__ volatile (".byte 0x48, 0x0f, 0xc7, 0xf0; setc %1" : "=a"(r1), "=q"(ok) :: "cc"); // rdrand %rax
        if (ok) break;
    }
    return r1;
#else
#error "RdRand is only supported on x86 and x86_64"
#endif
}

/** Read 64 bits of entropy using rdseed.
 *
 * Must only be called when RdSeed is supported.
 */
static uint64_t GetRdSeed() noexcept
{
    // RdSeed may fail when the HW RNG is overloaded. Loop indefinitely until enough entropy is gathered,
    // but pause after every failure.
#ifdef __i386__
    uint8_t ok;
    uint32_t r1, r2;
    do {
        __asm__ volatile (".byte 0x0f, 0xc7, 0xf8; setc %1" : "=a"(r1), "=q"(ok) :: "cc"); // rdseed %eax
        if (ok) break;
        __asm__ volatile ("pause");
    } while(true);
    do {
        __asm__ volatile (".byte 0x0f, 0xc7, 0xf8; setc %1" : "=a"(r2), "=q"(ok) :: "cc"); // rdseed %eax
        if (ok) break;
        __asm__ volatile ("pause");
    } while(true);
    return (((uint64_t)r2) << 32) | r1;
#elif defined(__x86_64__) || defined(__amd64__)
    uint8_t ok;
    uint64_t r1;
    do {
        __asm__ volatile (".byte 0x48, 0x0f, 0xc7, 0xf8; setc %1" : "=a"(r1), "=q"(ok) :: "cc"); // rdseed %rax
        if (ok) break;
        __asm__ volatile ("pause");
    } while(true);
    return r1;
#else
#error "RdSeed is only supported on x86 and x86_64"
#endif
}

>>>>>>> upstream/0.18
#else
static void RDRandInit() {}
#endif

<<<<<<< HEAD
static bool GetHWRand(unsigned char* ent32) {
#if defined(__x86_64__) || defined(__amd64__) || defined(__i386__)
    assert(hwrand_initialized.load(std::memory_order_relaxed));
    if (rdrand_supported) {
        uint8_t ok;
        // Not all assemblers support the rdrand instruction, write it in hex.
#ifdef __i386__
        for (int iter = 0; iter < 4; ++iter) {
            uint32_t r1, r2;
            __asm__ volatile (".byte 0x0f, 0xc7, 0xf0;" // rdrand %eax
                              ".byte 0x0f, 0xc7, 0xf2;" // rdrand %edx
                              "setc %2" :
                              "=a"(r1), "=d"(r2), "=q"(ok) :: "cc");
            if (!ok) return false;
            WriteLE32(ent32 + 8 * iter, r1);
            WriteLE32(ent32 + 8 * iter + 4, r2);
        }
#else
        uint64_t r1, r2, r3, r4;
        __asm__ volatile (".byte 0x48, 0x0f, 0xc7, 0xf0, " // rdrand %rax
                                "0x48, 0x0f, 0xc7, 0xf3, " // rdrand %rbx
                                "0x48, 0x0f, 0xc7, 0xf1, " // rdrand %rcx
                                "0x48, 0x0f, 0xc7, 0xf2; " // rdrand %rdx
                          "setc %4" :
                          "=a"(r1), "=b"(r2), "=c"(r3), "=d"(r4), "=q"(ok) :: "cc");
        if (!ok) return false;
        WriteLE64(ent32, r1);
        WriteLE64(ent32 + 8, r2);
        WriteLE64(ent32 + 16, r3);
        WriteLE64(ent32 + 24, r4);
=======
/** Add 64 bits of entropy gathered from hardware to hasher. Do nothing if not supported. */
static void SeedHardwareFast(CSHA512& hasher) noexcept {
#if defined(__x86_64__) || defined(__amd64__) || defined(__i386__)
    if (g_rdrand_supported) {
        uint64_t out = GetRdRand();
        hasher.Write((const unsigned char*)&out, sizeof(out));
        return;
    }
>>>>>>> upstream/0.18
#endif
}

/** Add 256 bits of entropy gathered from hardware to hasher. Do nothing if not supported. */
static void SeedHardwareSlow(CSHA512& hasher) noexcept {
#if defined(__x86_64__) || defined(__amd64__) || defined(__i386__)
    // When we want 256 bits of entropy, prefer RdSeed over RdRand, as it's
    // guaranteed to produce independent randomness on every call.
    if (g_rdseed_supported) {
        for (int i = 0; i < 4; ++i) {
            uint64_t out = GetRdSeed();
            hasher.Write((const unsigned char*)&out, sizeof(out));
        }
        return;
    }
    // When falling back to RdRand, XOR the result of 1024 results.
    // This guarantees a reseeding occurs between each.
    if (g_rdrand_supported) {
        for (int i = 0; i < 4; ++i) {
            uint64_t out = 0;
            for (int j = 0; j < 1024; ++j) out ^= GetRdRand();
            hasher.Write((const unsigned char*)&out, sizeof(out));
        }
        return;
    }
#endif
}

<<<<<<< HEAD
void RandAddSeed()
=======
/** Use repeated SHA512 to strengthen the randomness in seed32, and feed into hasher. */
static void Strengthen(const unsigned char (&seed)[32], int microseconds, CSHA512& hasher) noexcept
{
    CSHA512 inner_hasher;
    inner_hasher.Write(seed, sizeof(seed));

    // Hash loop
    unsigned char buffer[64];
    int64_t stop = GetTimeMicros() + microseconds;
    do {
        for (int i = 0; i < 1000; ++i) {
            inner_hasher.Finalize(buffer);
            inner_hasher.Reset();
            inner_hasher.Write(buffer, sizeof(buffer));
        }
        // Benchmark operation and feed it into outer hasher.
        int64_t perf = GetPerformanceCounter();
        hasher.Write((const unsigned char*)&perf, sizeof(perf));
    } while (GetTimeMicros() < stop);

    // Produce output from inner state and feed it to outer hasher.
    inner_hasher.Finalize(buffer);
    hasher.Write(buffer, sizeof(buffer));
    // Try to clean up.
    inner_hasher.Reset();
    memory_cleanse(buffer, sizeof(buffer));
}

static void RandAddSeedPerfmon(CSHA512& hasher)
>>>>>>> 3001cc61cf11e016c403ce83c9cbcfd3efcbcfd9
{
    // Seed with CPU performance counter
    int64_t nCounter = GetPerformanceCounter();
    RAND_add(&nCounter, sizeof(nCounter), 1.5);
    memory_cleanse((void*)&nCounter, sizeof(nCounter));
}

static void RandAddSeedPerfmon()
{
    RandAddSeed();

#ifdef WIN32
    // Don't need this on Linux, OpenSSL automatically uses /dev/urandom
    // Seed with the entire set of perfmon data

    // This can take up to 2 seconds, so only do it every 10 minutes
    static int64_t nLastPerfmon;
    if (GetTime() < nLastPerfmon + 10 * 60)
        return;
    nLastPerfmon = GetTime();

    std::vector<unsigned char> vData(250000, 0);
    long ret = 0;
    unsigned long nSize = 0;
    const size_t nMaxSize = 10000000; // Bail out at more than 10MB of performance data
    while (true) {
        nSize = vData.size();
        ret = RegQueryValueExA(HKEY_PERFORMANCE_DATA, "Global", nullptr, nullptr, vData.data(), &nSize);
        if (ret != ERROR_MORE_DATA || vData.size() >= nMaxSize)
            break;
        vData.resize(std::max((vData.size() * 3) / 2, nMaxSize)); // Grow size of buffer exponentially
    }
    RegCloseKey(HKEY_PERFORMANCE_DATA);
    if (ret == ERROR_SUCCESS) {
        RAND_add(vData.data(), nSize, nSize / 100.0);
        memory_cleanse(vData.data(), nSize);
        LogPrint(BCLog::RAND, "%s: %lu bytes\n", __func__, nSize);
    } else {
        static bool warned = false; // Warn only once
        if (!warned) {
            LogPrintf("%s: Warning: RegQueryValueExA(HKEY_PERFORMANCE_DATA) failed with code %i\n", __func__, ret);
            warned = true;
        }
    }
#endif
}

#ifndef WIN32
/** Fallback: get 32 bytes of system entropy from /dev/urandom. The most
 * compatible way to get cryptographic randomness on UNIX-ish platforms.
 */
static void GetDevURandom(unsigned char *ent32)
{
    int f = open("/dev/urandom", O_RDONLY);
    if (f == -1) {
        RandFailure();
    }
    int have = 0;
    do {
        ssize_t n = read(f, ent32 + have, NUM_OS_RANDOM_BYTES - have);
        if (n <= 0 || n + have > NUM_OS_RANDOM_BYTES) {
            close(f);
            RandFailure();
        }
        have += n;
    } while (have < NUM_OS_RANDOM_BYTES);
    close(f);
}
#endif

/** Get 32 bytes of system entropy. */
void GetOSRand(unsigned char *ent32)
{
#if defined(WIN32)
    HCRYPTPROV hProvider;
    int ret = CryptAcquireContextW(&hProvider, nullptr, nullptr, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT);
    if (!ret) {
        RandFailure();
    }
    ret = CryptGenRandom(hProvider, NUM_OS_RANDOM_BYTES, ent32);
    if (!ret) {
        RandFailure();
    }
    CryptReleaseContext(hProvider, 0);
#elif defined(HAVE_SYS_GETRANDOM)
    /* Linux. From the getrandom(2) man page:
     * "If the urandom source has been initialized, reads of up to 256 bytes
     * will always return as many bytes as requested and will not be
     * interrupted by signals."
     */
    int rv = syscall(SYS_getrandom, ent32, NUM_OS_RANDOM_BYTES, 0);
    if (rv != NUM_OS_RANDOM_BYTES) {
        if (rv < 0 && errno == ENOSYS) {
            /* Fallback for kernel <3.17: the return value will be -1 and errno
             * ENOSYS if the syscall is not available, in that case fall back
             * to /dev/urandom.
             */
            GetDevURandom(ent32);
        } else {
            RandFailure();
        }
    }
#elif defined(HAVE_GETENTROPY) && defined(__OpenBSD__)
    /* On OpenBSD this can return up to 256 bytes of entropy, will return an
     * error if more are requested.
     * The call cannot return less than the requested number of bytes.
       getentropy is explicitly limited to openbsd here, as a similar (but not
       the same) function may exist on other platforms via glibc.
     */
    if (getentropy(ent32, NUM_OS_RANDOM_BYTES) != 0) {
        RandFailure();
    }
#elif defined(HAVE_GETENTROPY_RAND) && defined(MAC_OSX)
    // We need a fallback for OSX < 10.12
    if (&getentropy != nullptr) {
        if (getentropy(ent32, NUM_OS_RANDOM_BYTES) != 0) {
            RandFailure();
        }
    } else {
        GetDevURandom(ent32);
    }
#elif defined(HAVE_SYSCTL_ARND)
    /* FreeBSD and similar. It is possible for the call to return less
     * bytes than requested, so need to read in a loop.
     */
    static const int name[2] = {CTL_KERN, KERN_ARND};
    int have = 0;
    do {
        size_t len = NUM_OS_RANDOM_BYTES - have;
        if (sysctl(name, ARRAYLEN(name), ent32 + have, &len, nullptr, 0) != 0) {
            RandFailure();
        }
        have += len;
    } while (have < NUM_OS_RANDOM_BYTES);
#else
    /* Fall back to /dev/urandom if there is no specific method implemented to
     * get system entropy for this OS.
     */
    GetDevURandom(ent32);
#endif
}

void GetRandBytes(unsigned char* buf, int num)
{
    if (RAND_bytes(buf, num) != 1) {
        RandFailure();
    }
}

static void AddDataToRng(void* data, size_t len);

void RandAddSeedSleep()
{
<<<<<<< HEAD
    int64_t nPerfCounter1 = GetPerformanceCounter();
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
    int64_t nPerfCounter2 = GetPerformanceCounter();
=======
    int64_t perfcounter = GetPerformanceCounter();
    hasher.Write((const unsigned char*)&perfcounter, sizeof(perfcounter));
}

static void SeedFast(CSHA512& hasher) noexcept
{
    unsigned char buffer[32];

    // Stack pointer to indirectly commit to thread/callstack
    const unsigned char* ptr = buffer;
    hasher.Write((const unsigned char*)&ptr, sizeof(ptr));

    // Hardware randomness is very fast when available; use it always.
    SeedHardwareFast(hasher);

    // High-precision timestamp
    SeedTimestamp(hasher);
}

static void SeedSlow(CSHA512& hasher) noexcept
{
    unsigned char buffer[32];

    // Everything that the 'fast' seeder includes
    SeedFast(hasher);

    // OS randomness
    GetOSRand(buffer);
    hasher.Write(buffer, sizeof(buffer));
>>>>>>> upstream/0.18

    // Combine with and update state
    AddDataToRng(&nPerfCounter1, sizeof(nPerfCounter1));
    AddDataToRng(&nPerfCounter2, sizeof(nPerfCounter2));

    memory_cleanse(&nPerfCounter1, sizeof(nPerfCounter1));
    memory_cleanse(&nPerfCounter2, sizeof(nPerfCounter2));
}

<<<<<<< HEAD
=======
/** Extract entropy from rng, strengthen it, and feed it into hasher. */
static void SeedStrengthen(CSHA512& hasher, RNGState& rng) noexcept
{
    static std::atomic<int64_t> last_strengthen{0};
    int64_t last_time = last_strengthen.load();
    int64_t current_time = GetTimeMicros();
    if (current_time > last_time + 60000000) { // Only run once a minute
        // Generate 32 bytes of entropy from the RNG, and a copy of the entropy already in hasher.
        unsigned char strengthen_seed[32];
        rng.MixExtract(strengthen_seed, sizeof(strengthen_seed), CSHA512(hasher), false);
        // Strengthen it for 10ms (100ms on first run), and feed it into hasher.
        Strengthen(strengthen_seed, last_time == 0 ? 100000 : 10000, hasher);
        last_strengthen = current_time;
    }
}

static void SeedSleep(CSHA512& hasher, RNGState& rng)
{
    // Everything that the 'fast' seeder includes
    SeedFast(hasher);
>>>>>>> 3001cc61cf11e016c403ce83c9cbcfd3efcbcfd9

static std::mutex cs_rng_state;
static unsigned char rng_state[32] = {0};
static uint64_t rng_counter = 0;

<<<<<<< HEAD
static void AddDataToRng(void* data, size_t len) {
    CSHA512 hasher;
    hasher.Write((const unsigned char*)&len, sizeof(len));
    hasher.Write((const unsigned char*)data, len);
    unsigned char buf[64];
    {
        std::unique_lock<std::mutex> lock(cs_rng_state);
        hasher.Write(rng_state, sizeof(rng_state));
        hasher.Write((const unsigned char*)&rng_counter, sizeof(rng_counter));
        ++rng_counter;
        hasher.Finalize(buf);
        memcpy(rng_state, buf + 32, 32);
    }
    memory_cleanse(buf, 64);
}

void GetStrongRandBytes(unsigned char* out, int num)
=======
    // Sleep for 1ms
    MilliSleep(1);

    // High-precision timestamp after sleeping (as we commit to both the time before and after, this measures the delay)
    SeedTimestamp(hasher);

    // Windows performance monitor data (once every 10 minutes)
    RandAddSeedPerfmon(hasher);

    // Strengthen every minute
    SeedStrengthen(hasher, rng);
}

static void SeedStartup(CSHA512& hasher, RNGState& rng) noexcept
>>>>>>> 3001cc61cf11e016c403ce83c9cbcfd3efcbcfd9
{
<<<<<<< HEAD
    assert(num <= 32);
    CSHA512 hasher;
    unsigned char buf[64];
=======
#ifdef WIN32
    RAND_screen();
#endif

    // Gather 256 bits of hardware randomness, if available
    SeedHardwareSlow(hasher);

    // Everything that the 'slow' seeder includes.
    SeedSlow(hasher);

    // Windows performance monitor data.
    RandAddSeedPerfmon(hasher);

    // Strengthen
    SeedStrengthen(hasher, rng);
}

enum class RNGLevel {
    FAST, //!< Automatically called by GetRandBytes
    SLOW, //!< Automatically called by GetStrongRandBytes
    SLEEP, //!< Called by RandAddSeedSleep()
};
>>>>>>> upstream/0.18

    // First source: OpenSSL's RNG
    RandAddSeedPerfmon();
    GetRandBytes(buf, 32);
    hasher.Write(buf, 32);

    // Second source: OS RNG
    GetOSRand(buf);
    hasher.Write(buf, 32);

<<<<<<< HEAD
    // Third source: HW RNG, if available.
    if (GetHWRand(buf)) {
        hasher.Write(buf, 32);
    }

    // Combine with and update state
    {
        std::unique_lock<std::mutex> lock(cs_rng_state);
        hasher.Write(rng_state, sizeof(rng_state));
        hasher.Write((const unsigned char*)&rng_counter, sizeof(rng_counter));
        ++rng_counter;
        hasher.Finalize(buf);
        memcpy(rng_state, buf + 32, 32);
=======
    CSHA512 hasher;
    switch (level) {
    case RNGLevel::FAST:
        SeedFast(hasher);
        break;
    case RNGLevel::SLOW:
        SeedSlow(hasher);
        break;
    case RNGLevel::SLEEP:
        SeedSleep(hasher, rng);
        break;
    }

    // Combine with and update state
    if (!rng.MixExtract(out, num, std::move(hasher), false)) {
        // On the first invocation, also seed with SeedStartup().
        CSHA512 startup_hasher;
        SeedStartup(startup_hasher, rng);
        rng.MixExtract(out, num, std::move(startup_hasher), true);
>>>>>>> 3001cc61cf11e016c403ce83c9cbcfd3efcbcfd9
    }

    // Produce output
    memcpy(out, buf, num);
    memory_cleanse(buf, 64);
}

uint64_t GetRand(uint64_t nMax)
{
    if (nMax == 0)
        return 0;

    // The range of the random source must be a multiple of the modulus
    // to give every possible output value an equal possibility
    uint64_t nRange = (std::numeric_limits<uint64_t>::max() / nMax) * nMax;
    uint64_t nRand = 0;
    do {
        GetRandBytes((unsigned char*)&nRand, sizeof(nRand));
    } while (nRand >= nRange);
    return (nRand % nMax);
}

int GetRandInt(int nMax)
{
    return GetRand(nMax);
}

uint256 GetRandHash()
{
    uint256 hash;
    GetRandBytes((unsigned char*)&hash, sizeof(hash));
    return hash;
}

void FastRandomContext::RandomSeed()
{
    uint256 seed = GetRandHash();
    rng.SetKey(seed.begin(), 32);
    requires_seed = false;
}

uint256 FastRandomContext::rand256()
{
    if (bytebuf_size < 32) {
        FillByteBuffer();
    }
    uint256 ret;
    memcpy(ret.begin(), bytebuf + 64 - bytebuf_size, 32);
    bytebuf_size -= 32;
    return ret;
}

std::vector<unsigned char> FastRandomContext::randbytes(size_t len)
{
    std::vector<unsigned char> ret(len);
    if (len > 0) {
        rng.Keystream(&ret[0], len);
    }
    return ret;
}

FastRandomContext::FastRandomContext(const uint256& seed) : requires_seed(false), bytebuf_size(0), bitbuf_size(0)
{
    rng.SetKey(seed.begin(), 32);
}

bool Random_SanityCheck()
{
    uint64_t start = GetPerformanceCounter();

    /* This does not measure the quality of randomness, but it does test that
     * OSRandom() overwrites all 32 bytes of the output given a maximum
     * number of tries.
     */
    static const ssize_t MAX_TRIES = 1024;
    uint8_t data[NUM_OS_RANDOM_BYTES];
    bool overwritten[NUM_OS_RANDOM_BYTES] = {}; /* Tracks which bytes have been overwritten at least once */
    int num_overwritten;
    int tries = 0;
    /* Loop until all bytes have been overwritten at least once, or max number tries reached */
    do {
        memset(data, 0, NUM_OS_RANDOM_BYTES);
        GetOSRand(data);
        for (int x=0; x < NUM_OS_RANDOM_BYTES; ++x) {
            overwritten[x] |= (data[x] != 0);
        }

        num_overwritten = 0;
        for (int x=0; x < NUM_OS_RANDOM_BYTES; ++x) {
            if (overwritten[x]) {
                num_overwritten += 1;
            }
        }

        tries += 1;
    } while (num_overwritten < NUM_OS_RANDOM_BYTES && tries < MAX_TRIES);
    if (num_overwritten != NUM_OS_RANDOM_BYTES) return false; /* If this failed, bailed out after too many tries */

    // Check that GetPerformanceCounter increases at least during a GetOSRand() call + 1ms sleep.
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
    uint64_t stop = GetPerformanceCounter();
    if (stop == start) return false;

    // We called GetPerformanceCounter. Use it as entropy.
    RAND_add((const unsigned char*)&start, sizeof(start), 1);
    RAND_add((const unsigned char*)&stop, sizeof(stop), 1);

    return true;
}

FastRandomContext::FastRandomContext(bool fDeterministic) : requires_seed(!fDeterministic), bytebuf_size(0), bitbuf_size(0)
{
    if (!fDeterministic) {
        return;
    }
    uint256 seed;
    rng.SetKey(seed.begin(), 32);
}

void RandomInit()
{
    RDRandInit();
}
