
//
// DISCLAIMER
// 
// THIS SOFTWARE IS PROVIDED "AS IS" FOR NON-COMMERCIAL RESEARCH USE ONLY.
// ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
// THE IMPLIED WARRANTIES OF MERCHANTABILITY
// AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
// THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
// INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//

//
// File: featInputMM.cpp
// Author: Matthew Toews (matt.toews@gmail.com)
// Description:
//	- Basic input of 3D scale-invariant features (Toews and Wells, MIA 2013)
//	- Function to 'invert' feature geometry and appearance descriptor
//		due to local linear intenstiy inversion (Toews, Zöllei & Wells, IPMI 2013)
//

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>

#define DESCRIPTOR_SIZE 64

//
// Feature3DInfo
//
// Class for 3D scale invariant feature.
//
class Feature3DInfo
{

public:

	~Feature3DInfo() {};

	Feature3DInfo() {};

	// 
	// DistSqr()
	//
	// Squared Euclidean distance between two descriptors.
	//
	int
	DistSqr(
		Feature3DInfo &feat3D
	)
	{
		int iSumSqr = 0;
		for( int i = 0; i < DESCRIPTOR_SIZE; i++ )
		{
			int iDiff = (m_pucDesc[i] - feat3D.m_pucDesc[i]);
			iSumSqr += iDiff*iDiff;
		}
		return iSumSqr;	 
	}

	// Information flags regarding this feature
	unsigned int	m_uiInfo;

	// Defines wether feature corresponds to a DOG minima (0) or maxima (1)
#define INFO_FLAG_MIN0MAX1 0x00000010

	// Defines whether feature appearance has been reoriented, yes (1) or no (0)
#define INFO_FLAG_REORIENT 0x00000020


	// Location
	float x;
	float y;
	float z;

	// Scale
	float scale;

	// Orientation axes (major to minor)
	float ori[3][3];

	// Eigenvalues of second moment matrix (major to minor)
	float eigs[3];

	// Data fields: added to support different data descriptors
	unsigned char m_pucDesc[DESCRIPTOR_SIZE];
};

//
// feature3DInput()
//
// Reads the 3D features in file pcFileName.
// Allocates and stores features in *ppFeats.
// Sets *piFeatCount to the number of features read.
// Returns 0 in success, negative on failure.
//
int
feature3DInput(
				  Feature3DInfo **ppFeats,
				  int *piFeatCount,
				  char *pcFileName
)
{
	FILE *infile = fopen( pcFileName, "rt" );
	if( !infile )
	{
		return -2;
	}

	int &iFeatCount = *piFeatCount;
	*ppFeats = 0;
	iFeatCount = 0;

	char buff[400];
	char vers[400];
	buff[0] = '#';

	// Read past comments
	while( buff[0] == '#' )
	{
		fgets( buff, sizeof(buff), infile );
		// Look for version number
		if( sscanf(buff, "# featExtract %s\n", vers ) == 1 )
		{
			printf( "File created using featExtract version: %s\n", vers );
		}
	}

	if( sscanf( buff, "Features: %d\n", &iFeatCount ) <= 0 || iFeatCount <= 0 )
	{
		fclose( infile );
		return -3;
	}
	fgets( buff, sizeof(buff), infile );
	if( strstr( buff, "Scale-space location[x y z scale] orientation[o11 o12 o13 o21 o22 o23 o31 o32 o32] 2nd moment eigenvalues[e1 e2 e3] info flag[i1] descriptor[d1 .. d64]" ) == 0 )
	{
		fclose( infile );
		return -4;
	}

	Feature3DInfo *pFeats3D;
	pFeats3D = new Feature3DInfo[ iFeatCount ];
	if( !pFeats3D )
	{
		fclose( infile );
		return -1;
	}
	*ppFeats = pFeats3D;

	for( int i = 0; i < iFeatCount; i++ )
	{
		int iReturn = 
			fscanf( infile, "%f\t%f\t%f\t%f\t", &(pFeats3D[i].x), &(pFeats3D[i].y), &(pFeats3D[i].z), &(pFeats3D[i].scale) );
		assert( iReturn == 4 );

		for( int j = 0; j < 3; j++ )
		{
			for( int k = 0; k < 3; k++ )
			{
				iReturn = fscanf( infile, "%f\t", &(pFeats3D[i].ori[j][k]) );
				assert( iReturn == 1 );
			}
		}

		// Eigenvalues of 2nd moment matrix
		for( int j = 0; j < 3; j++ )
		{
			iReturn = fscanf( infile, "%f\t", &(pFeats3D[i].eigs[j]) );
			assert( iReturn == 1 );
		}

		// Info flag
		iReturn = fscanf( infile, "%d\t", &(pFeats3D[i].m_uiInfo) );
		assert( iReturn == 1 );

		// Descriptor
		for( int j = 0; j < DESCRIPTOR_SIZE; j++ )
		{
			int iValue;
			iReturn = fscanf( infile, "%d\t", &iValue );
			assert( iReturn == 1 );
			assert( iValue >= 0 );
			assert( iValue < DESCRIPTOR_SIZE );
			pFeats3D[i].m_pucDesc[j] = iValue;
		}
	}

	fclose( infile );

	return 0;
}

//
// findNearestNeighborsBruteForce()
//
// Compute nearest neighbor descriptor matches between two arrays of features.
//
// pfFeats1: array 1 of features, length iCount1
// pfFeats2: array 2 of features, length iCount2
// piMatchIndices: array of nearest neighbor matches, length iCount1
//
// Notes: Brute force matching is used here for simplicity, much more efficient
//        matching algorithms exist, e.g. KD-tree lookup.
//		  Geometrical consistency checks can be used to filter incorrect
//        matches, e.g. the Hough transform.
//
int
findNearestNeighborsBruteForce(
				  Feature3DInfo *pFeats1, int iCount1,
				  Feature3DInfo *pFeats2, int iCount2,
				  int *piMatchIndices
					 )
{
	for( int i1 = 0; i1 < iCount1; i1++ )
	{
		int iMinIndex = 0;
		int iMinDistSqr = pFeats1[i1].DistSqr( pFeats2[0] );
		for( int i2 = 1; i2 < iCount2; i2++ )
		{
			int iDistSqr = pFeats1[i1].DistSqr( pFeats2[i2] );
			if( iDistSqr < iMinDistSqr )
			{
				iMinIndex = i2;
				iMinDistSqr = iDistSqr;
			}
		}
		piMatchIndices[i1] = iMinIndex;
	}

	return 0;
}

//
// msInvertIntensity()
//
// This function transforms feature geometry & appearance descriptor for 
// multi-modal image correspondence, assuming a local intensity inversion.
//
// It is used for matching features across local intensity inversions,
// i.e. T2 and T1 MR modalities.
// 
// Described in the following publication:
//   Matthew Toews, Lilla Zöllei, William M. Wells III,
//   "Invariant Feature-based Alignment of Volumetric Multi-modal Images",
//   Information Processing in Medical Imaging (IPMI) 2013
//
//	 www.matthewtoews.com/papers/ipmi13-matt-final.pdf
//
int
msInvertIntensity(
					Feature3DInfo &feat
					)
{
	// 1) Rotate first two orientation vectors by 180°
	for( int i = 0; i < 2; i++ )
	{
		for( int j = 0; j < 3; j++ )
		{
			feat.ori[i][j] = -feat.ori[i][j];
		}
	}

	// 2) Re-order descriptor indices to account for orientation change
	unsigned char chIndices[DESCRIPTOR_SIZE] = {25,	24,	27,	26,	29,	28,	31,	30,	17,	16,	19,	18,	21,	20,	23,	22,	9,	8,	11,	10,	13,	12,	15,	14,	1,	0,	3,	2,	5,	4,	7,	6,	57,	56,	59,	58,	61,	60,	63,	62,	49,	48,	51,	50,	53,	52,	55,	54,	41,	40,	43,	42,	45,	44,	47,	46,	33,	32,	35,	34,	37,	36,	39,	38 };
	float pfTemp[DESCRIPTOR_SIZE];

	for( int i = 0; i < DESCRIPTOR_SIZE; i++ )
	{
		pfTemp[i] = feat.m_pucDesc[i];
	}
	for( int i = 0; i < DESCRIPTOR_SIZE; i++ )
	{
		feat.m_pucDesc[i] = pfTemp[ chIndices[i] ];
	}

	return 1;
}


int
main(
	 int argc,
	 char **argv
)
{
	if( argc != 2 )
	{
		printf( "Demo program to read in 3D feature files.\n" );
		printf( "Usage: %s <input feature file>\n", argv[0] );
		return -27182;
	}

	Feature3DInfo *pFeats;
	int iFeatCount;
	int iReturn;
	try
	{
		iReturn = feature3DInput( &pFeats, &iFeatCount, argv[1] );
	}
	catch(...)
	{
		printf( "Error reading input feature file: argv[1]\n" );
		return -31415;
	}

	if( iReturn != 0 )
	{
		printf( "Error reading input feature file: %d\n", iReturn );
		return iReturn;
	}

	printf( "Features read: %d\n", iFeatCount );

	// Allocate an array for nearest neighbor matching
	int *piNearestNeighbors = new int[iFeatCount];
	if( !piNearestNeighbors )
	{
		printf( "Error: could not allocate array to test nearest neighbor matching.\n" );
		delete [] pFeats;
		return  -14142;
	}

	// For testing:
	//  - invert intensity of one feature
	msInvertIntensity( pFeats[0] );
	//  - invert it back
	msInvertIntensity( pFeats[0] );


	// Match feature array to itself
	printf( "Matching self-test: " );
	findNearestNeighborsBruteForce( pFeats, iFeatCount, pFeats, iFeatCount, piNearestNeighbors );

	int iError = 0;
	for( int i = 0; i < iFeatCount; i++ )
	{
		if( piNearestNeighbors[i] != i )
		{
			iError = 1;
		}
	}

	iError == 0 ? printf( "passed.\n" ) : printf( "failed.\n" );

	printf( "done.\n" );

	delete [] piNearestNeighbors;
	delete [] pFeats;

	return 0;
}
